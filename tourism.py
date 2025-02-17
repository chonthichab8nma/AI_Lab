from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextBrowser
from rdflib import Graph
from tkinter import messagebox

class OntologySearch:
    def __init__(self, ontology_file):
        # โหลดไฟล์ RDF/OWL
        self.g = Graph()
        self.g.parse(ontology_file, format="xml")

    def search_info(self, keyword):
        # สร้าง SPARQL query เพื่อค้นหาจังหวัดที่เกี่ยวข้องกับคำค้น
        query = f"""
            PREFIX : <http://www.my_ontology.edu/mytourism#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?subject ?property ?value WHERE {{
                ?subject ?property ?value .
                FILTER (
                    regex(str(?subject), "{keyword}", "i") || 
                    regex(str(?value), "{keyword}", "i") || 
                    regex(str(?property), "{keyword}", "i") ||
                    regex(str(?subject), "{keyword.lower()}", "i") || 
                    regex(str(?value), "{keyword.lower()}", "i") || 
                    regex(str(?property), "{keyword.lower()}", "i")
                )
                FILTER (?property IN (:hasFlower, :hasImageOfProvince, :hasLatitudeOfProvince, :hasLongitudeOfProvince, :hasMotto, :hasNameOfProvince, :hasSeal, :hasTraditionalNameOfProvince, :hasTree, :hasURLOfProvince))
            }}
        """

        results = self.g.query(query)
        data = {}

        for row in results:
            subject = str(row.subject).split("#")[-1]
            property_name = str(row.property).split("#")[-1]
            value = str(row.value)

             # ตรวจสอบว่ามีข้อมูลที่ซ้ำหรือไม่ ถ้ามีให้ไม่เพิ่มเข้าไป
        if subject not in data:
            data[subject] = {}

        # ตรวจสอบว่าค่าของ property นี้มีแล้วหรือไม่ ถ้ามีให้ไม่เพิ่มซ้ำ
        if property_name not in data[subject]:
            data[subject][property_name] = []

        if value not in data[subject][property_name]:
            data[subject][property_name].append(value)
        return data
   


    def get_full_info(self, subject):
        # สร้าง SPARQL query เพื่อดึงข้อมูลทั้งหมดของจังหวัดที่พบ
        query = f"""
            PREFIX : <http://www.my_ontology.edu/mytourism#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?property ?value WHERE {{
                :{subject} ?property ?value .
                FILTER (?property IN (:hasFlower, :hasImageOfProvince, :hasLatitudeOfProvince, :hasLongitudeOfProvince, :hasMotto, :hasNameOfProvince, :hasSeal, :hasTraditionalNameOfProvince, :hasTree, :hasURLOfProvince))
            }}
        """

        results = self.g.query(query)
        full_data = []

        for row in results:
            property_name = str(row.property).split("#")[-1]
            value = str(row.value)
            full_data.append(f"🔹 {property_name}: {value}")

        return full_data

class ProvinceSearchApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ค้นหาข้อมูลจังหวัด")

        # โหลด Ontology
        try:
            self.ontology_search = OntologySearch("tourism.owl")  # ปรับใช้การค้นหาด้วย rdflib
        except FileNotFoundError:
            print("ไม่พบไฟล์ tourism.owl")
            self.close()  # ปิดแอปหากไม่พบไฟล์
            return

        # สร้าง UI
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("พิมพ์คำค้นหา")
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("ค้นหา", self)
        self.search_button.clicked.connect(self.search)
        layout.addWidget(self.search_button)

        #self.clear_button = QPushButton("เคลียร์ข้อมูล", self)
        #self.clear_button.clicked.connect(self.clear_results)
        #layout.addWidget(self.clear_button)

        self.result_box = QTextBrowser(self)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def search(self):
        province_name = self.search_input.text()
        self.result_box.clear()  # ล้างผลลัพธ์เก่า

        # ค้นหาข้อมูลจาก Ontology
        data = self.ontology_search.search_info(province_name)

        if data:
            for subject, properties in data.items():
                self.result_box.append(f"📍 {subject}:\n")
                for property in properties:
                    self.result_box.append(f"  {property}\n")

                full_info = self.ontology_search.get_full_info(subject)
                if full_info:
                    self.result_box.append("\nข้อมูลทั้งหมดของจังหวัด:\n")
                    self.result_box.append("\n".join(full_info))
                self.result_box.append("\n")
        else:
            self.result_box.append("ไม่พบข้อมูลจังหวัด")

    def clear_results(self):
        self.result_box.clear()

if __name__ == "__main__":
    app = QApplication([])
    window = ProvinceSearchApp()
    window.show()
    app.exec()
