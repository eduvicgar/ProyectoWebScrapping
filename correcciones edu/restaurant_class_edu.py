from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from typing import List, Dict, Tuple
import datetime
import re


class Restaurant:
    def __init__(self, driver: webdriver, url_restaurante: str) -> None:
        self.driver: webdriver = driver
        self.url: str = url_restaurante
        self.driver.get(self.url)

    def fetch_restaurant_data(self):
        sleep(5) # Esperamos a que se cargue toda la página
        restaurant = dict()
        restaurant["Name"] = self.get_name()
        restaurant["Address"] = self.get_address()
        coordinates = self.get_coordinates() 
        restaurant["Lat"] = coordinates[0]
        restaurant["Long"] = coordinates[1]
        restaurant["Number of Ratings"] = self.get_total_rating()
        restaurant["Restaurant Rating"] = self.get_rating()
        restaurant["Type of Restaurant"] = self.get_type_restaurant()
        restaurant["Number of Bookmarks"] = self.get_bookmarks()
        restaurant["Price Range"] = self.get_price_range()
        restaurant["Phone Number"] = self.get_telephone_number()
        restaurant["Website"] = self.get_restaurant_website()
        restaurant["Instagram"] = self.get_instagram()
        restaurant["Facebook"] = self.get_facebook()
        restaurant["Timetable"] = self.get_timetable()

        return restaurant
        

    def get_name(self) -> str:
        # Pablo
        try:
            titulo = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
                (By.XPATH, "//h1[@class='header-title text-2xl leading-normal break-words md:text-[1.75rem]  ']")))

            return titulo.get_attribute("textContent")

        except Exception as e:
            print(f"Error al obtener el nombre: {e}")

    def get_address(self) -> str:
        # Edu
        try:
            calle = self.driver.find_element(By.XPATH, "//span[@itemprop='streetAddress']").get_attribute("textContent")
            ciudad = self.driver.find_element(By.XPATH, "//span[@itemprop='addressLocality']").get_attribute("textContent")
            pais = self.driver.find_element(By.XPATH, "//span[@itemprop='addressCountry']").get_attribute("textContent")
            codigo_postal = self.driver.find_element(By.XPATH, "//span[@itemprop='postalCode']").get_attribute("textContent")

            direccion = calle + ", " + ciudad + ", " + pais + ", " + codigo_postal
            return direccion
        except Exception as e:
            print(f"Error al obtener la dirección: {e}")

    def get_coordinates(self) -> Tuple[str, str]:
        # Anton
        try:
            map_path: str = '//*[@id="full-site-content"]//div[@class="relative rounded-xl overflow-hidden border border-gray-300 max-h-[120px] sm:max-h-[170px] md:mt-[84px] md:max-h-[200px]"]/a'
            map_element = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, map_path)))

            href: str = map_element.get_attribute("href")

            pattern: str = r"(?P<lat>-?[0-9]+\.[0-9]+),(?P<long>-?[0-9]+\.[0-9]+)"
            coordinates: re.Match = re.search(pattern, href)
            lat: str = coordinates.group("lat")
            long: str = coordinates.group("long")
            return lat, long
        except Exception as e:
            print(f"Error al obtener las coordenadas: {e}")


    def get_total_rating(self) -> int:
        # Edu
        try:
            ratings = self.driver.find_elements(By.XPATH, "//span[@class='rating-reviews leading-7 text-sm text-gray-500 ml-0']")
            if not ratings:
                return 0
            else:
                ratings_limpio = re.sub(r"[()]", "", ratings[0].text)
                return int(ratings_limpio)
        except Exception as e:
            print(f"Error al obtener el número de reviews: {e}")

    def get_rating(self) -> float:
        # Edu
        try:
            valoracion = self.driver.find_elements(By.XPATH, "//meta[@itemprop='ratingValue']")
            if not valoracion:
                return 0
            else:
                return float(valoracion[0].get_attribute("content"))
        except Exception as e:
            print(f"Error al obtener la valoración: {e}")

    def get_type_restaurant(self) -> List[str]:
        # Pablo + revisión Edu
        """
        A lo mejor hay que crear funciones auxiliares que filtran los diferentes tipos de restaurantes
        """
        types = ["Korean", "African", "American", "Asian", "Australian", "Brazilian", "British", "Caribbean", "Chinese", "European", "French", "Fusion", "German", "Indian", "International", "Italian", "Japanese", "Latin", "Mediterranean", "Mexican", "Middle Eastern", "Spanish", "Taiwanese", "Thai", "Vietnamese", "Western"]
        try:
            type_res = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="full-site-content"]/div[3]/div[2]/div/div[1]/article/div/div')))
            list_type: List[str] = []
            for i in type_res:
                if i.text in types and i.text != "Vegan":
                    list_type += [i.text]
            return list_type

        except Exception as e:
            print(f"Error al obtener el tipo de restaurante: {e}")

    def get_bookmarks(self) -> int:
        # Anton + revisión Edu
        try:
            path: str = '//ul[@class="md:order-0 lg:-mt-1"]//span[@class="favorite-badge leading-7 align-middle inline-flex text-sm text-gray-500"]'
            bookmarks = self.driver.find_elements(By.XPATH, path)
            if not bookmarks:
                return 0
            else:
                return int(bookmarks[0].get_attribute("textContent"))
        except Exception as e:
            print(f"Error al obtener el número de guardados: {e}")



    def get_price_range(self) -> str:
        # Edu
        """
        Crear una función auxiliar que convierte los iconos dollars a: Cheap, Medium, Expensive (o lo que sea)
        """
        try:
            cantidad_dolares = self.driver.find_elements(By.XPATH, "//*[@class='h-4.5 w-4.5 -mx-0.5 text-yellow-500']")
            if len(cantidad_dolares) == 1:
                return "Barato"
            elif len(cantidad_dolares) == 2:
                return "Moderado"
            elif len(cantidad_dolares) == 3:
                return "Caro"
            else:
                return "No price range"
        except Exception as e:
            print(f"Error al obtener el rango de precio: {e}")

    def get_telephone_number(self) -> str:
    # Pablo + revisión Edu
    # ¡NO Siempre funciona!
    # Ejemplo: "https://www.happycow.net/reviews/relish-bar-madrid-388770"
    # Corregido
        path: str = "//span[@itemprop = 'telephone']"
        try:
            telefono = self.driver.find_elements(By.XPATH, path)
            if not telefono:
                return "No phone number"
            else:
                return telefono[0].get_attribute("textContent")
        except Exception as e:
            print(f"Error al obtener el número de teléfono: {e}")


    def get_restaurant_website(self) -> str:
        # Anton + revisión Edu
        website_path: str = '//a[contains(text(), "Website")]'
        try:
            website = self.driver.find_elements(By.XPATH, website_path)
            if not website:
                return "No website"
            else:
                website_link = website[0].get_attribute("href")
                return website_link
        except Exception as e:
            print(f"Error al obtener la web del restaurante: {e}")



    def get_instagram(self) -> str:
        # Revisión Edu
        instagram_path: str = '//a[contains(text(), "Instagram")]'
        try:
            instagram = self.driver.find_elements(By.XPATH, instagram_path)
            if not instagram:
                return "No instagram"
            else:
                instagram_link = instagram[0].get_attribute("href")
                return instagram_link
        except Exception as e:
            print(f"Error al obtener el instagram: {e}")
        

    
    
    def get_facebook(self) -> str:
        # Anton + revisión Edu
        facebook_path: str = '//a[contains(text(), "Facebook")]'
        try:
            facebook = self.driver.find_elements(By.XPATH, facebook_path)
            if not facebook:
                return "No facebook"
            else:
                facebook_link = facebook[0].get_attribute("href")
                return facebook_link
        except Exception as e:
            print(f"Error al obtener el facebook: {e}")
        

    def get_timetable(self) -> Dict[str, str]:
        # Revisión Edu
        # TODO ¡¡En algunas páginas no funciona!!
        try:
            horario_dict = dict()
            dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for dia in dias:
                horario_dict.setdefault(dia, "Closed")
            boton_expandir = self.driver.find_elements(By.XPATH,
                                                  "//a[@class = 'btn-toggle-hours flex items-center text-primary-500 group hover:text-primary-300 transition-color duration-200 ease-in-out']")
            if not boton_expandir:
                return {"Horario": "No hay horario"}
            else:
                boton_expandir[1].click()
                horario_html = self.driver.find_elements(By.XPATH,
                                                    "//ul[@class = 'hours-list group flex flex-col open']/child::*")
                for elem in horario_html:
                    dia = elem.find_element(By.XPATH, "./p[@class = 'hours-day group-[.open]:w-[105px]']")
                    horas = elem.find_element(By.XPATH, "./div")
                    horas_limpio = horas.text.replace("\n",
                                                    ", ")  # Si el establecimiento tiene horario partido aparecerá un salto de línea entre las dos franjas horarias.
                    if dia.text == "Today":
                        horario_dict[datetime.datetime.today().strftime("%A")] = horas_limpio
                    else:
                        horario_dict[dia.text] = horas_limpio
                return horario_dict

        except Exception as e:
            print(f"Error al obtener el horario: {e}")