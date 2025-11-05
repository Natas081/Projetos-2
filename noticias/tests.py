
import os
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

from .models import Noticia, Interest, DiarioEntry, CheckIn, Goal
from datetime import date, timedelta
from django.utils import timezone # ★ Importar timezone

# ===================================================================
# CLASSE BASE DE TESTE
# ===================================================================

class TestInterfaceUsuario(StaticLiveServerTestCase):
    MAIN_H1_SELECTOR = (By.CSS_SELECTOR, "main h1")

    @classmethod
    def setUpClass(cls):
        """
        Configura o driver do Selenium UMA VEZ para toda a classe de teste.
        ★ AGORA DETECTA O MODO CI (HEADLESS) ★
        """
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        
        options = webdriver.ChromeOptions()
        
        # Verifica se está rodando no ambiente de CI (GitHub Actions)
        if os.environ.get('CI') == 'true':
            print("Rodando em modo CI (Headless)...")
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080') # Define um tamanho de janela
        else:
            # Rodando localmente (mostra o navegador)
            print("Rodando localmente (com navegador visível)...")
            options.add_argument("--start-maximized")
        
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.wait = WebDriverWait(cls.driver, 10) # Espera explícita de 10s

    @classmethod
    def tearDownClass(cls):
        print("\nTestes concluídos. Fechando o navegador.")
        time.sleep(3)
        cls.driver.quit()
        super().tearDownClass()

    
    def setUp(self):
        super().setUp()
        self.username = 'usuarioteste'
        self.password = 'senha1234'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        self.driver.get(f'{self.live_server_url}/login/')
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(self.username)
        time.sleep(0.5)
        self.driver.find_element(By.NAME, 'password').send_keys(self.password)
        time.sleep(0.5)
        login_button_xpath = "//div[contains(@class, 'sign-in')]//button[contains(., 'Entrar')]"
        self.driver.find_element(By.XPATH, login_button_xpath).click()
        self.wait.until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, 'h2'), "Seu Progresso de Leitura"
        ))
        print(f"\nSetup: Usuário '{self.username}' logado e pronto para o teste.")
        time.sleep(1)

# ===================================================================
# TESTES DE FLUXO
# ===================================================================

    def test_fluxo_interesses_e_rotina(self):
        print("Iniciando: test_fluxo_interesses_e_rotina")
        driver = self.driver
        
        driver.find_element(By.PARTIAL_LINK_TEXT, "Interesses").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Seus Interesses"))
        print("Navegou para a página de Interesses.")
        time.sleep(1)

        nome_interesse = "Testes Automatizados"
        driver.find_element(By.NAME, 'name').send_keys(nome_interesse)
        time.sleep(0.5)
        driver.find_element(By.NAME, 'target_frequency').send_keys("2")
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//button[contains(., 'Adicionar')]").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Interesse \"Testes Automatizados\" adicionado!"))
        xpath_segunda_msg = "//div[contains(@class, 'bg-green-100') and contains(text(), 'Meta semanal criada: 2 leituras.')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_segunda_msg)))
        print("Interesse e Meta criados com sucesso.")
        time.sleep(1)
        
        driver.find_element(By.PARTIAL_LINK_TEXT, "Rotina").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Rotina Semanal"))
        print("Navegou para a página de Rotina.")
        time.sleep(1)

        meta_xpath = f"//li[contains(., '{nome_interesse}')]"
        self.assertTrue(
            EC.text_to_be_present_in_element((By.XPATH, f"{meta_xpath}//p[contains(., 'Progresso: 0 / 2')]"), "Progresso: 0 / 2")(driver),
            "Texto 'Progresso: 0 / 2' não encontrado."
        )
        print("Verificado: Progresso inicial é 0/2.")

        # --- ★ CORREÇÃO V9 (BOTÃO) ★ ---
        # Acha o botão de "Marcar leitura" pelo XPath combinado (LI + classe do botão)
        button_xpath = f"//li[contains(., '{nome_interesse}')]//button[contains(@class, 'bg-red-600')]"
        self.wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()

        # 6. VERIFICA O PROGRESSO 1/2
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Progresso atualizado"))
        self.assertTrue(
            EC.text_to_be_present_in_element((By.XPATH, f"{meta_xpath}//p[contains(., 'Progresso: 1 / 2')]"), "Progresso: 1 / 2")(driver),
             "Texto 'Progresso: 1 / 2' não encontrado após o primeiro clique."
        )
        print("Progresso 1/2 marcado.")
        time.sleep(1.5)

        # 7. MARCA A LEITURA (2ª vez)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()

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
        print("Iniciando: test_fluxo_streak")
        driver = self.driver
        widget = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fixed")))
        self.assertIn("0 dia(s)", widget.text)
        print("Verificado: Streak inicial no widget é 0.")
        
        widget.find_element(By.TAG_NAME, 'a').click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Seu Streak de Leitura"))
        print("Navegou para a página de Streak.")
        time.sleep(1)

        checkin_button = driver.find_element(By.XPATH, "//button[contains(., 'Confirmar acesso de hoje')]")
        checkin_button.click()
        
        # (views.py: messages.success(request, f"Check-in diário confirmado! Seu streak é {perfil.leitura_streak} dias.")
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Check-in diário confirmado!"))
        print("Verificado: Mensagem de check-in OK.")
        
        xpath_confirmacao_streak = "//p[contains(@class, 'text-green-600') and contains(text(), 'Você já confirmou o acesso hoje')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_confirmacao_streak)))
        print("Verificado: Botão de check-in desapareceu e texto de confirmação apareceu.")
        
        streak_text = driver.find_element(By.CSS_SELECTOR, 'span.text-4xl').text
        self.assertIn("1", streak_text)
        print("Verificado: Contagem de streak na página é 1.")
        
        print("Teste de fluxo (Streak) concluído!")
        time.sleep(2)


    def test_fluxo_diario_completo(self):
        print("Iniciando: test_fluxo_diario_completo")
        driver = self.driver
        
        driver.find_element(By.PARTIAL_LINK_TEXT, "Diário").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Diário do Aprendizado"))
        print("Navegou para a página do Diário.")
        
        self.assertIn("Nenhuma anotação ainda", driver.find_element(By.TAG_NAME, 'body').text)
        time.sleep(1)

        texto_original = "Hoje aprendi a configurar testes com Selenium."
        driver.find_element(By.NAME, 'texto').send_keys(texto_original)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar Anotação')]").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação salva no diário!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), texto_original))
        print("Verificado: Anotação original criada.")
        time.sleep(1)

        driver.find_element(By.XPATH, "//a[contains(., 'Editar')]").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Editar Anotação"))
        print("Navegou para a página de Edição.")
        time.sleep(1)

        texto_editado = "Hoje aprendi a editar anotações."
        textarea = driver.find_element(By.NAME, 'texto')
        textarea.clear()
        textarea.send_keys(texto_editado)
        time.sleep(1)
        # (editar_anotacao.html: <button ...>Salvar Alterações</button>)
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar Alterações')]").click()

        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação atualizada com sucesso!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), texto_editado))
        self.assertNotIn(texto_original, driver.find_element(By.TAG_NAME, 'body').text)
        print("Verificado: Anotação editada com sucesso.")
        time.sleep(1)

        driver.find_element(By.XPATH, "//button[contains(., 'Excluir')]").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação removida com sucesso!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Nenhuma anotação ainda"))
        self.assertNotIn(texto_editado, driver.find_element(By.TAG_NAME, 'body').text)
        print("Verificado: Anotação excluída com sucesso.")

        print("Teste de fluxo (Diário) concluído!")
        time.sleep(2)
        
    # ===================================================================
    # ★ TESTES DO RESUMO SEMANAL (COM CORREÇÕES DE DATA) ★
    # ===================================================================

    def test_resumo_semanal_cenario_3_novo_usuario(self):
        print("Iniciando: test_resumo_semanal_cenario_3 (Novo Usuário)")
        driver = self.driver
        
        driver.find_element(By.PARTIAL_LINK_TEXT, "Resumo Semanal").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Resumo Semanal"))
        print("Navegou para a página de Resumo.")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Resumo semanal disponível após 7 dias de uso", body_text)
        print("Verificado: Mensagem de '7 dias' exibida corretamente.")
        time.sleep(1)

    def test_resumo_semanal_cenario_2_sem_atividade(self):
        print("Iniciando: test_resumo_semanal_cenario_2 (Sem Atividade)")
        driver = self.driver

        # --- ★ CORREÇÃO V9 (DATA) ★ ---
        # Força a data de criação do CheckIn para 8 dias atrás,
        # contornando o 'auto_now_add=True'
        oito_dias_atras = timezone.localdate() - timedelta(days=8)
        CheckIn.objects.create(usuario=self.user, data_checkin=oito_dias_atras)
        # Atualiza o objeto recém-criado (auto_now_add pode ter prioridade)
        CheckIn.objects.filter(usuario=self.user).update(data_checkin=oito_dias_atras)
        print("Usuário 'envelhecido' 8 dias.")

        driver.find_element(By.PARTIAL_LINK_TEXT, "Resumo Semanal").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Resumo Semanal"))
        print("Navegou para a página de Resumo.")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Nenhuma novidade nesta semana", body_text)
        print("Verificado: Mensagem 'Nenhuma novidade' exibida corretamente.")
        time.sleep(1)

    def test_resumo_semanal_cenario_1_com_atividade(self):
        print("Iniciando: test_resumo_semanal_cenario_1 (Com Atividade)")
        driver = self.driver
        
        # --- ★ CORREÇÃO V9 (DATA) ★ ---
        oito_dias_atras = timezone.localdate() - timedelta(days=8)
        CheckIn.objects.create(usuario=self.user, data_checkin=oito_dias_atras)
        CheckIn.objects.filter(usuario=self.user).update(data_checkin=oito_dias_atras)
        
        week_start = Goal.get_start_of_week()
        
        interest_astro = Interest.objects.create(user=self.user, name="Astronomia")
        Goal.objects.create(user=self.user, interest=interest_astro, targetFrequency=5, currentProgress=3, weekStartDate=week_start)
        
        interest_hist = Interest.objects.create(user=self.user, name="História")
        Goal.objects.create(user=self.user, interest=interest_hist, targetFrequency=2, currentProgress=1, weekStartDate=week_start)

        DiarioEntry.objects.create(usuario=self.user, texto="Minha anotação da semana")
        print("Usuário 'envelhecido' e atividades da semana criadas.")

        driver.find_element(By.PARTIAL_LINK_TEXT, "Resumo Semanal").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Resumo Semanal"))
        print("Navegou para a página de Resumo.")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, 'body').text
        
        self.assertIn("Novos Interesses", body_text)
        self.assertIn("Astronomia", body_text)
        self.assertIn("História", body_text)
        
        self.assertIn("Interesse Mais Ativo", body_text)
        self.assertIn("Astronomia — 3 leituras", body_text)
        
        self.assertIn("Anotações da Semana", body_text)
        self.assertIn("Minha anotação da semana", body_text)
        
        print("Verificado: Todas as atividades da semana exibidas corretamente.")
        time.sleep(2)