from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebElement

import os
import time
from datetime import date
import shutil
from typing import Union, List


class InstagramScraper:
    """
    Classe para realizar o download de relatários do Instagram.

    Atributos:
        username (str): nome de usuário do Instagram.
        password (str): senha do Instagram.

    Métodos:
        __init__(self, username, password): inicializa a classe.
        get_driver(self): retorna o driver do navegador.
        get_element(self, xpath, force_waiting=False, origin_element=False, multiple=False): obtém um elemento da pagina.
        login(self): realiza o login no Instagram.
        go_to_insights(self): navega para a página de insights.
        export_data(self): configura preferências de exportação.
        wait_and_download(self): aguarda processamento e realiza o download.
        move_and_rename_file(self): renomeia e move o arquivo de download.
        extraction_routine(self): executa a rotina de extração.
    """

    URL_LOGIN = "https://business.facebook.com"
    URL_INSIGHTS = "https://business.facebook.com/latest/insights/content"
    DOWNLOAD_PATH = os.path.join(os.getcwd(), "temp")
    XPATH_BUTTON_LOGIN_WITH_INSTAGRAM = (
        """//button[contains(text(), 'Log in with Instagram')]"""
    )
    XPATH_INPUT_USERNAME = """//*[@id="loginForm"]/div/div[1]/div/label/input"""
    XPATH_INPUT_PASSWORD = """//*[@id="loginForm"]/div/div[2]/div/label/input"""
    XPATH_BUTTON_LOGIN = """//*[@id="loginForm"]/div/div[3]/button/div"""
    XPATH_CONTAINER_SAVE_INFO = """//div[contains(text(), 'Save your login info?')]"""
    XPATH_ICON_META = """//i[contains(@alt, 'Meta Business Suite')]"""
    XPATH_BUTTON_EXPORT = """//div[contains(text(), 'Export data')]"""
    XPATH_MODAL_EXPORT = """//*[@id="facebook"]/body/div[3]/div[1]/div[1]/div"""
    XPATH_BUTTON_INSTAGRAM = """//span[contains(text(), 'Instagram')]"""
    XPATH_COMBO_ACCOUNT = """//div[@role='combobox']"""
    XPATH_OPTION_SELECT_ALL = """//div[contains(text(), 'Select all')]"""
    XPATH_OPTION_STORIES = """//div[contains(text(), 'Data for story posts')]"""
    XPATH_BUTTON_GENERATE = """//div[contains(text(), 'Generate')]"""
    # XPATH_BUTTON_DOWNLOAD = """//div[contains(text(), 'Download export')]"""
    XPATH_BUTTON_DOWNLOAD = (
        """//div[contains(text(), 'Download export')]/../../../../../div"""
    )

    def __init__(self, username, password):
        """
        Inicializa a instância da classe InstagramScraper.

        Args:
            username (str): nome de usuário do Instagram.
            password (str): senha do Instagram.
        """

        self.username = username
        self.password = password
        self.driver = self.get_driver()

    def get_driver(self):
        """
        Inicia o driver do navegador.

        Returns:
            webdriver: driver do navegador.
        """

        if not os.path.exists(self.DOWNLOAD_PATH):
            os.makedirs(self.DOWNLOAD_PATH)

        options = Options()
        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self.DOWNLOAD_PATH,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
            },
        )
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def get_element(
        self,
        xpath: str,
        force_waiting: bool = False,
        origin_element: Union[bool, WebElement] = False,
        multiple: bool = False,
    ):
        """
        Obtém um elemento da pagina.

        Args:
            xpath (str): xpath do elemento.
            force_waiting (bool, optional): aguarda o elemento estar visível. Defaults to False.
            origin_element (bool or WebElement, optional): elemento de origem. Defaults to False.
            multiple (bool, optional): retorna uma lista. Defaults to False.

        Returns:
            Union[WebElement, List[WebElement]]: Elemento ou lista de elementos da página.
        """

        if force_waiting and not multiple:
            return WebDriverWait(
                (self.driver if not origin_element else origin_element), 10
            ).until(EC.element_to_be_clickable((By.XPATH, xpath)))

        elif multiple:
            return (
                self.driver if not origin_element else origin_element
            ).find_elements(By.XPATH, xpath)

        else:
            return (self.driver if not origin_element else origin_element).find_element(
                By.XPATH, xpath
            )

    def login(self):
        """
        Realiza o login no Bussiness Facebook.
        """

        self.driver.get(self.URL_LOGIN)
        self.get_element(
            xpath=self.XPATH_BUTTON_LOGIN_WITH_INSTAGRAM, force_waiting=True
        ).click()
        self.get_element(xpath=self.XPATH_INPUT_USERNAME, force_waiting=True).send_keys(
            self.username
        )
        self.get_element(xpath=self.XPATH_INPUT_PASSWORD).send_keys(self.password)
        self.get_element(xpath=self.XPATH_BUTTON_LOGIN).click()
        self.get_element(xpath=self.XPATH_CONTAINER_SAVE_INFO, force_waiting=True)

        self.driver.get(self.URL_LOGIN)
        self.get_element(
            xpath=self.XPATH_BUTTON_LOGIN_WITH_INSTAGRAM, force_waiting=True
        ).click()
        self.get_element(xpath=self.XPATH_ICON_META, force_waiting=True)

    def go_to_insights(self):
        """
        Navega para o painel de Insights.
        """
        self.driver.get(self.URL_INSIGHTS)

    def export_data(self, option: str):
        """
        Inicia a rotina de exportação.

        Args:
            option (str): Tipo de exportação:stories / posts.
        """

        self.get_element(force_waiting=True, xpath=self.XPATH_BUTTON_EXPORT).click()

        element_modal = self.get_element(
            force_waiting=True, xpath=self.XPATH_MODAL_EXPORT
        )

        self.get_element(
            xpath=self.XPATH_BUTTON_INSTAGRAM,
            origin_element=element_modal,
        ).click()

        if option == "stories":
            self.get_element(
                xpath=self.XPATH_OPTION_STORIES, origin_element=element_modal
            ).click()

        self.get_element(
            xpath=self.XPATH_BUTTON_GENERATE, origin_element=element_modal
        ).click()

    def wait_and_download(self):
        """
        Aguarda processamento e realiza o download.
        """

        # element_button = self.get_element(xpath=self.XPATH_BUTTON_DOWNLOAD, force_waiting=True)

        elapsed_time = 0

        while True:
            element_button = self.get_element(
                xpath=self.XPATH_BUTTON_DOWNLOAD,
                force_waiting=True,
            )

            button_disabled = element_button.get_attribute("aria-disabled")

            if button_disabled == "true":
                print("Tempo total de espera:", elapsed_time, "segundos")
                time.sleep(15)
                elapsed_time += 15
            else:
                print("Processamento concluído! Realizando download...")
                element_button.click()
                break

    def move_and_rename_file(self, file_type: str):
        """
        Move e renomeia o arquivo de download.

        Args:
            file_type (str): tipo de arquivo: stories / posts.

        Raises:
            Exception: caso ocorra algum erro ao mover o arquivo.
        """
        origin = self.DOWNLOAD_PATH + "\\" + os.listdir(self.DOWNLOAD_PATH)[0]

        destination = (
            os.getcwd()
            + f"\\scraper\\exports\\{file_type}_{date.today().strftime('%m-%d-%Y')}.csv"
        )

        try:
            shutil.move(origin, destination)

        except Exception as e:
            print("Ocorreu um erro ao mover o arquivo:", e)

    def extraction_routine(self):
        """
        Executa a rotina de extração.
        """
        print("Iniciando extracao")
        print("Logando")
        self.login()
        print("Acessando Insights")
        self.go_to_insights()

        print("Configurando exportação para stories")
        self.export_data(option="stories")
        print("Aguardando processamento e realizando download")
        self.wait_and_download()
        print("Movendo e renomeando o arquivo")
        self.move_and_rename_file(file_type="stories")

        print("Configurando exportação para posts")
        self.export_data(option="posts")
        print("Aguardando processamento e realizando download")
        self.wait_and_download()
        print("Movendo e renomeando o arquivo")
        self.move_and_rename_file(file_type="posts")

        print("Extração Finalizada")
