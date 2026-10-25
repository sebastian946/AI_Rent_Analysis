from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


LIST_URL_RENT_PAGES = {
    "FINCARAIZ": "https://www.fincaraiz.com.co/"
}


class WebScraping:
    def __init__(self, price, square_meters, vehicles, department, ubication,
                 property_type, service_type, headless: bool = False):
        self.price = price
        self.square_meters = square_meters
        self.vehicles = vehicles
        self.department = department
        self.ubication = ubication
        self.property_type = property_type
        self.service_type = service_type
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page_browser = None

    def get_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page_browser = self.browser.new_page()
        return self.page_browser

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def scraping_page(self):
        if self.page_browser is None:
            self.get_browser()
        for key, url in LIST_URL_RENT_PAGES.items():
            if key == "FINCARAIZ":
                self.scraping_fincaraiz(url)

    def scraping_fincaraiz(self, url):
        print(f"[FINCARAIZ] Open Url {url} ...")
        self.page_browser.goto(url)
        self.page_browser.wait_for_load_state("domcontentloaded")
        print(f"[FINCARAIZ] Titulo de la pagina: {self.page_browser.title()}")

        if not self.select_property_type_fincaraiz():
            return None

        if not self.select_type_service():
            return None

        self.input_location()
        self.click_search_button()
        return self.get_info()

    def select_type_service(self) -> bool:
        """Selecciona el tipo de operacion (Arriendo / Venta) en el filtro."""
        content = self.page_browser.locator(".operation-type-filter")
        try:
            content.wait_for(state="visible", timeout=10000)
        except PlaywrightTimeoutError:
            return self.error_handling_locator(".operation-type-filter")

        # El filtro es un radio group de Ant Design: cada opcion es un label
        buttons = content.locator("label.ant-radio-button-wrapper")
        available = [t.strip() for t in buttons.all_inner_texts() if t.strip()]

        target = next((t for t in available if t.lower() == self.service_type.lower()), None)
        if target is None:
            print(f"[FINCARAIZ] Tipo de servicio '{self.service_type}' no existe. Disponibles: {available}")
            return False

        # Se hace click en el label completo: el <span> con el texto esta tapado
        # por el overlay .ant-radio-button y el click directo sobre el se bloquea
        buttons.filter(has_text=target).click()

        selected = content.locator(".ant-radio-button-wrapper-checked").all_inner_texts()
        print(f"[FINCARAIZ] Tipo de servicio seleccionado: {selected}")
        return selected == [target]

    def select_property_type_fincaraiz(self) -> bool:
        """Abre el select de tipo de inmueble y elige la opcion segun property_type."""
        option_label = self.property_type.capitalize()  

        self.page_browser.click(".ant-select-selector")

        dropdown = self.page_browser.locator(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
        )
        try:
            dropdown.wait_for(state="visible", timeout=10000)
        except PlaywrightTimeoutError:
            print("[FINCARAIZ] No se abrio la lista de tipo de inmueble")
            return False

        options = dropdown.locator(".ant-select-item-option")
        available = [o.get_attribute("title") for o in options.all()]

        if option_label not in available:
            print(f"[FINCARAIZ] Opcion '{option_label}' no existe. Disponibles: {available}")
            return False

        for option in options.all():
            title = option.get_attribute("title")
            is_selected = "ant-select-item-option-selected" in (option.get_attribute("class") or "")
            should_select = title == option_label

            if is_selected != should_select:
                option.click()

        self.page_browser.keyboard.press("Escape")  # cierra el dropdown
        selected = self.page_browser.locator(".ant-select-selection-item").all_inner_texts()
        print(f"[FINCARAIZ] Tipo de inmueble seleccionado: {selected}")
        return selected == [option_label]

    def input_location(self):
        location_input = ".location-search__input"

        if not self.page_browser.locator(location_input):
            self.error_handling_locator(location_input)
        self.page_browser.locator(location_input).fill(self.ubication)

    # Click search button page
    def click_search_button(self):
        location_button = ".search-button"
        location_cards = ".listingsWrapper"

        if not self.page_browser.locator(location_button):
            self.error_handling_locator(location_button)

        self.page_browser.locator(location_button).click()

        if not self.page_browser.locator(location_cards):
            self.error_handling_locator(location_cards)

    def get_info(self):
        cards = self.page_browser.locator(".lc-dataWrapper")
        cards.first.wait_for(state="visible", timeout=10000)  

        results = []
        for card in cards.all():
            detail = card.locator("a").first 
            href = detail.get_attribute("href")
            title = detail.get_attribute("title")

            price = detail.locator(".main-price").inner_text()

            # Varios <strong> (habitaciones, banos, m2): all_inner_texts devuelve una lista
            distribution = detail.locator(
                '//div[@class="lc-typologyContainer"]//span/strong'
            ).all_inner_texts()

            location = detail.locator(".lc-title").inner_text()     

            description = detail.locator(".lc-description").inner_text()
            results.append({
                "url": href,
                "title": title,
                "price": price,
                "distribution": distribution,
                "location": location,
                "description": description
            })
        return results


    # Error Handlings
    def error_handling_locator(self,locator):
        print(f"The locator {locator} not found in the page")
        return False





def test_run():
    """Prueba rapida: abre el navegador, entra a cada portal y lo cierra."""
    scraper = WebScraping(
        price="2000000",
        square_meters="60",
        vehicles=1,
        department="Antioquia",
        ubication="Medellin",
        property_type="apartamento",
        service_type="arriendo",
        headless=False,
    )
    try:
        scraper.scraping_page()
        input("Presiona Enter para cerrar el navegador...")
    finally:
        scraper.close()


if __name__ == "__main__":
    test_run()
