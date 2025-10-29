# Em /noticias/tests.py

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Importamos os modelos que serão necessários
from .models import Noticia, Interest, DiarioEntry

# ===================================================================
# CLASSE BASE DE TESTE
# ===================================================================

class TestInterfaceUsuario(StaticLiveServerTestCase):
    """
    Testes End-to-End (E2E) para o projeto MeuJornal.
    """

    @classmethod
    def setUpClass(cls):
        """
        Configura o driver do Selenium UMA VEZ para toda a classe de teste.
        """
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        
        # Opções para garantir que o navegador apareça visível
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.wait = WebDriverWait(cls.driver, 10) # Espera explícita de 10s


    @classmethod
    def tearDownClass(cls):
        """
        Fecha o driver UMA VEZ após todos os testes da classe rodarem.
        """
        print("\nTestes concluídos. Fechando o navegador.")
        time.sleep(3) # Pausa final para ver o último estado
        cls.driver.quit()
        super().tearDownClass()

    
    def setUp(self):
        """
        Executa ANTES DE CADA TESTE ('test_...').
        Cria um usuário de teste e faz o login.
        """
        super().setUp()
        
        # 1. Cria um usuário de teste
        self.username = 'usuarioteste'
        self.password = 'senha1234'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        
        # 2. FAZ O LOGIN (usando a nova URL e template)
        self.driver.get(f'{self.live_server_url}/login/')
        self.wait.until(EC.presence_of_element_located((By.ID, 'id_username'))).send_keys(self.username)
        time.sleep(0.5)
        self.driver.find_element(By.ID, 'id_password').send_keys(self.password)
        time.sleep(0.5)
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 3. VERIFICA O REDIRECIONAMENTO
        self.wait.until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, 'h2'), "Seu Progresso de Leitura"
        ))
        print(f"\nSetup: Usuário '{self.username}' logado e pronto para o teste.")
        time.sleep(1) # Pausa para ver a página inicial

# ===================================================================
# TESTES DE FLUXO
# ===================================================================

    def test_fluxo_interesses_e_rotina(self):
            """
            Testa o fluxo:
            1. Criar um Interesse com Meta.
            2. Ir para Rotina e marcar a leitura desse interesse.
            """
            print("Iniciando: test_fluxo_interesses_e_rotina")
            driver = self.driver

            # 1. NAVEGA PARA A PÁGINA DE INTERESSES
            driver.find_element(By.PARTIAL_LINK_TEXT, "Interesses").click()
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Seus Interesses"))
            print("Navegou para a página de Interesses.")
            time.sleep(1)

            # 2. ADICIONA NOVO INTERESSE E META
            nome_interesse = "Testes Automatizados"
            driver.find_element(By.NAME, 'name').send_keys(nome_interesse)
            time.sleep(0.5)
            driver.find_element(By.NAME, 'target_frequency').send_keys("2")
            time.sleep(0.5)
            driver.find_element(By.XPATH, "//button[contains(., 'Adicionar')]").click()

            # 3. VERIFICA O RESULTADO
            self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Interesse \"Testes Automatizados\" adicionado!"))
            xpath_segunda_msg = "//div[contains(@class, 'bg-green-100') and contains(text(), 'Meta semanal criada: 2 leituras.')]"
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_segunda_msg)))
            print("Interesse e Meta criados com sucesso.")
            time.sleep(1)

            # 4. VAI PARA A PÁGINA DE ROTINA
            driver.find_element(By.PARTIAL_LINK_TEXT, "Rotina").click()
            self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Rotina Semanal"))
            print("Navegou para a página de Rotina.")
            time.sleep(1)

            # 5. ENCONTRA A META E VERIFICA O PROGRESSO INICIAL (0/2)
            meta_xpath = f"//li[contains(., '{nome_interesse}')]"
            goal_element = self.wait.until(EC.presence_of_element_located((By.XPATH, meta_xpath)))
            self.assertTrue(
                EC.text_to_be_present_in_element((By.XPATH, f"{meta_xpath}//p[contains(., 'Progresso: 0 / 2')]"), "Progresso: 0 / 2")(driver),
                "Texto 'Progresso: 0 / 2' não encontrado."
            )
            print("Verificado: Progresso inicial é 0/2.")

            # ★ CORREÇÃO 1 ★
            # Usa seletor CSS para encontrar o botão DENTRO do 'goal_element'
            button_selector = "form button[type='submit']"
            goal_element.find_element(By.CSS_SELECTOR, button_selector).click()

            # 6. VERIFICA O PROGRESSO 1/2
            self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Progresso atualizado"))
            self.assertTrue(
                EC.text_to_be_present_in_element((By.XPATH, f"{meta_xpath}//p[contains(., 'Progresso: 1 / 2')]"), "Progresso: 1 / 2")(driver),
                "Texto 'Progresso: 1 / 2' não encontrado após o primeiro clique."
            )
            print("Progresso 1/2 marcado.")
            time.sleep(1.5)

            # 7. MARCA A LEITURA (2ª vez)
            # ★ CORREÇÃO 2 ★
            # Reencontra o LI e usa o mesmo seletor CSS para o botão
            goal_element = self.wait.until(EC.presence_of_element_located((By.XPATH, meta_xpath))) # Reencontra o elemento LI
            goal_element.find_element(By.CSS_SELECTOR, button_selector).click() # Usa o mesmo seletor CSS

            # 8. VERIFICA O PROGRESSO 2/2 (META ATINGIDA)
            self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Progresso atualizado"))
            self.assertTrue(
                EC.text_to_be_present_in_element((By.XPATH, f"{meta_xpath}//span[contains(., 'Meta atingida')]"), "Meta atingida")(driver),
                "Texto 'Meta atingida' não encontrado após o segundo clique."
            )
            print("Progresso 2/2 (Meta Atingida) marcado.")

            print("Teste de fluxo (Interesses e Rotina) concluído!")
            time.sleep(2)


    def test_fluxo_streak(self):
        """
        Testa o fluxo de check-in diário na página de Streak.
        """
        print("Iniciando: test_fluxo_streak")
        driver = self.driver

        # 1. VERIFICA O STREAK INICIAL NO WIDGET
        widget = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fixed")))
        self.assertIn("0 dia(s)", widget.text)
        print("Verificado: Streak inicial no widget é 0.")
        
        # 2. VAI PARA A PÁGINA DE STREAK
        widget.find_element(By.TAG_NAME, 'a').click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Seu Streak de Leitura"))
        print("Navegou para a página de Streak.")
        time.sleep(1)

        # 3. CLICA NO BOTÃO DE CHECK-IN
        checkin_button = driver.find_element(By.XPATH, "//button[contains(., 'Confirmar acesso de hoje')]")
        checkin_button.click()

        # 4. VERIFICA O RESULTADO
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Check-in confirmado com sucesso!"))
        print("Verificado: Mensagem de check-in OK.")
        
        # ★ CORREÇÃO 2 ★
        # (streak.html: <p class="text-green-600 ...">Você já confirmou o acesso hoje! 🎉</p>)
        # Usamos um seletor CSS mais específico para o parágrafo de confirmação
        xpath_confirmacao_streak = "//p[contains(@class, 'text-green-600') and contains(text(), 'Você já confirmou o acesso hoje')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_confirmacao_streak)))
        print("Verificado: Botão de check-in desapareceu e texto de confirmação apareceu.")
        
        # Verifica se o streak na página atualizou para 1
        streak_text = driver.find_element(By.CSS_SELECTOR, 'span.text-4xl').text
        self.assertIn("1", streak_text)
        print("Verificado: Contagem de streak na página é 1.")
        
        print("Teste de fluxo (Streak) concluído!")
        time.sleep(2)


    def test_fluxo_diario_completo(self):
        """
        Testa o fluxo completo do Diário:
        1. Criar uma anotação.
        2. Editar a anotação.
        3. Excluir a anotação.
        """
        print("Iniciando: test_fluxo_diario_completo")
        driver = self.driver
        
        # 1. VAI PARA A PÁGINA DO DIÁRIO
        driver.find_element(By.PARTIAL_LINK_TEXT, "Diário").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Diário do Aprendizado"))
        print("Navegou para a página do Diário.")
        
        self.assertIn("Nenhuma anotação ainda", driver.find_element(By.TAG_NAME, 'body').text)
        time.sleep(1)

        # 2. CRIA UMA NOVA ANOTAÇÃO
        texto_original = "Hoje aprendi a configurar testes com Selenium."
        driver.find_element(By.NAME, 'texto').send_keys(texto_original)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar Anotação')]").click()
        
        # 3. VERIFICA A CRIAÇÃO
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação salva no diário!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), texto_original))
        print("Verificado: Anotação original criada.")
        time.sleep(1)

        # 4. CLICA EM EDITAR
        driver.find_element(By.XPATH, "//a[contains(., 'Editar')]").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h1'), "Editar Anotação"))
        print("Navegou para a página de Edição.")
        time.sleep(1)

        # 5. EDITA A ANOTAÇÃO
        texto_editado = "Hoje aprendi a editar anotações."
        textarea = driver.find_element(By.NAME, 'texto')
        textarea.clear()
        textarea.send_keys(texto_editado)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar Alterações')]").click()

        # 6. VERIFICA A EDIÇÃO
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação atualizada com sucesso!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), texto_editado))
        self.assertNotIn(texto_original, driver.find_element(By.TAG_NAME, 'body').text)
        print("Verificado: Anotação editada com sucesso.")
        time.sleep(1)

        # 7. CLICA EM EXCLUIR
        driver.find_element(By.XPATH, "//button[contains(., 'Excluir')]").click()
        
        # 8. VERIFICA A EXCLUSÃO
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação removida com sucesso!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Nenhuma anotação ainda"))
        self.assertNotIn(texto_editado, driver.find_element(By.TAG_NAME, 'body').text)
        print("Verificado: Anotação excluída com sucesso.")

        print("Teste de fluxo (Diário) concluído!")
        time.sleep(2)