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
    """

    LOGIN_URL = "https://business.facebook.com"
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
    XPATH_FLASH_STATUS = """//div[@data-testid="ContextualLayerRoot"]"""
    XPATH_FLASH_HEADER = """//div[@role='heading']"""
    XPATH_BUTTON_DOWNLOAD = """//div[contains(text(), 'Download export')]"""

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
        Realiza o login no Instagram.
        """

        self.driver.get(self.LOGIN_URL)
        self.get_element(
            force_waiting=True, xpath=self.XPATH_BUTTON_LOGIN_WITH_INSTAGRAM
        ).click()
        self.get_element(xpath=self.XPATH_INPUT_USERNAME).send_keys(self.username)
        self.get_element(xpath=self.XPATH_INPUT_PASSWORD).send_keys(self.password)
        self.get_element(xpath=self.XPATH_BUTTON_LOGIN).click()
        self.get_element(xpath=self.XPATH_CONTAINER_SAVE_INFO, force_waiting=True)

    def go_to_insights(self):
        """
        Navega para o painel de Insights.
        """

        self.driver.get(self.LOGIN_URL)
        self.get_element(
            xpath=self.XPATH_BUTTON_LOGIN_WITH_INSTAGRAM, force_waiting=True
        ).click()
        self.get_element(xpath=self.XPATH_ICON_META, force_waiting=True)
        self.driver.get("https://business.facebook.com/latest/insights/content")

    def export_data(self):
        """
        Configura as preferências de exportação.
        """

        self.get_element(force_waiting=True, xpath=self.XPATH_BUTTON_EXPORT).click()

        element_modal = self.get_element(
            force_waiting=True, xpath=self.XPATH_MODAL_EXPORT
        )

        self.get_element(
            xpath=self.XPATH_BUTTON_INSTAGRAM,
            origin_element=element_modal,
        ).click()

        element_combo_accounts = self.get_element(
            xpath=self.XPATH_COMBO_ACCOUNT, multiple=True
        )[-1]

        element_combo_accounts.click()

        self.get_element(
            xpath=self.XPATH_OPTION_SELECT_ALL, origin_element=element_combo_accounts
        ).click()

        element_combo_accounts.click()

        self.get_element(
            xpath=self.XPATH_OPTION_STORIES, origin_element=element_combo_accounts
        ).click()

        self.get_element(
            xpath=self.XPATH_BUTTON_GENERATE, origin_element=element_modal
        ).click()

    def wait_and_download(self):
        """
        Aguarda processamento e realiza o download.
        """

        element_flash_status = self.get_element(
            xpath=self.XPATH_FLASH_STATUS, force_waiting=True
        )
        waiting_time = 0

        while True:
            progress_status = (
                self.get_element(
                    xpath=self.XPATH_FLASH_HEADER,
                    origin_element=element_flash_status,
                    multiple=True,
                )[2]
                .find_element(By.XPATH, "./following-sibling::*")
                .text.split(" • ")[-1]
            )

            if progress_status == "100%":
                print("Concluido")
                break
            else:
                print(f"Aguardando processamento - tempo total {waiting_time}s")
                waiting_time += 10
                time.sleep(10)

        self.get_element(xpath=self.XPATH_BUTTON_DOWNLOAD).click()
        time.sleep(10)

    def move_and_rename_file(self):
        """
        Renomeia e move o arquivo de download.

        Raises:
            Exception: caso ocorra algum erro ao mover o arquivo.
        """
        origin = self.DOWNLOAD_PATH + "\\" + os.listdir(self.DOWNLOAD_PATH)[0]

        destination = (
            os.getcwd()
            + f"\\scraper\\exports\\stories_{date.today().strftime('%m-%d-%Y')}.csv"
        )

        try:
            shutil.move(origin, destination)

        except Exception as e:
            print("Ocorreu um erro ao mover o arquivo:", e)
