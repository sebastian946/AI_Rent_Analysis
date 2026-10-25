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
        # No se usa `with sync_playwright()` porque al salir del bloque
        # se cierra el navegador y la página deja de servir.
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

    def select_property_type_fincaraiz(self) -> bool:
        """Abre el select de tipo de inmueble y elige la opcion segun property_type."""
        option_label = self.property_type.capitalize()  # "casa" -> "Casa"

        self.page_browser.click(".ant-select-selector")

        # Ant Design deja el dropdown en el DOM al cerrarlo y solo le agrega la
        # clase -hidden, por eso se excluye. El div "#rc_select_X_list" es solo
        # para accesibilidad y siempre esta oculto: no sirve para esperar.
        dropdown = self.page_browser.locator(
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
        )
        try:
            dropdown.wait_for(state="visible", timeout=10000)
        except PlaywrightTimeoutError:
            print("[FINCARAIZ] No se abrio la lista de tipo de inmueble")
            return False

        # Los elementos role="option" tambien existen dentro del listbox oculto
        # de accesibilidad, asi que se usa la clase del item visual y su title.
        options = dropdown.locator(".ant-select-item-option")
        available = [o.get_attribute("title") for o in options.all()]
        if option_label not in available:
            print(f"[FINCARAIZ] Opcion '{option_label}' no existe. Disponibles: {available}")
            return False

        # El select es de seleccion multiple y trae "Casa" y "Apartamento"
        # marcados por defecto. Cada click alterna la opcion, asi que se
        # recorre la lista y se deja marcada unicamente la deseada.
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
