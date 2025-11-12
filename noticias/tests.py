# Em /noticias/tests.py (VERSÃO FINAL COMPLETA)

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

# --- ★ IMPORTS ATUALIZADOS ★ ---
from .models import Noticia, Interest, DiarioEntry, CheckIn, Goal, Categoria, UserProfile
from datetime import date, timedelta
from django.utils import timezone
# --- ★ FIM DOS IMPORTS ★ ---


# ===================================================================
# CLASSE BASE DE TESTE
# ===================================================================

class TestInterfaceUsuario(StaticLiveServerTestCase):
    # (By.TAG_NAME, 'h1') é ambíguo. Usamos (By.CSS_SELECTOR, "main h1")
    MAIN_H1_SELECTOR = (By.CSS_SELECTOR, "main h1")

    @classmethod
    def setUpClass(cls):
        """
        Configura o driver do Selenium UMA VEZ para toda a classe de teste.
        Detecta o modo CI (Headless).
        """
        super().setUpClass()
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        
        if os.environ.get('CI') == 'true':
            print("Rodando em modo CI (Headless)...")
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
        else:
            print("Rodando localmente (com navegador visível)...")
            options.add_argument("--start-maximized")
        
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        print("\nTestes concluídos. Fechando o navegador.")
        time.sleep(3)
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
        # (O signal em models.py cria automaticamente o UserProfile e o Perfil)

        # --- ★ CORREÇÃO CRÍTICA (HISTÓRIA 1) ★ ---
        # A view 'home' agora REDIRECIONA se o usuário não seguir nenhuma categoria.
        # Para que os testes antigos funcionem, precisamos fazer o usuário
        # seguir uma categoria "padrão" durante o setUp.
        cat_padrao = Categoria.objects.create(nome="Geral")
        self.user.userprofile.categorias_seguidas.add(cat_padrao)
        # --- FIM DA CORREÇÃO ---

        # 2. FAZ O LOGIN
        self.driver.get(f'{self.live_server_url}/login/')
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(self.username)
        time.sleep(0.5)
        self.driver.find_element(By.NAME, 'password').send_keys(self.password)
        time.sleep(0.5)
        login_button_xpath = "//div[contains(@class, 'sign-in')]//button[contains(., 'Entrar')]"
        self.driver.find_element(By.XPATH, login_button_xpath).click()
        
        # 3. VERIFICA O REDIRECIONAMENTO
        # --- ★ CORREÇÃO CRÍTICA (HTML) ★ ---
        # (O H2 de 'home.html' mudou de 'Seu Progresso de Leitura' para 'Dashboard - MeuJornal')
        self.wait.until(EC.text_to_be_present_in_element(
            (By.TAG_NAME, 'h2'), "Dashboard - MeuJornal"
        ))
        print(f"\nSetup: Usuário '{self.username}' logado e pronto para o teste.")
        time.sleep(1) # Pausa para ver a página inicial

# ===================================================================
# TESTES ANTIGOS (AGORA FUNCIONANDO)
# ===================================================================

    def test_fluxo_interesses_e_rotina(self):
        """
        Testa a funcionalidade ANTIGA de Interesses (NÃO o filtro de temas)
        """
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

        button_xpath = f"//li[contains(., '{nome_interesse}')]//button[contains(@class, 'bg-red-600')]"
        self.wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()

        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Progresso atualizado"))
        self.assertTrue(
            EC.text_to_be_present_in_element((By.XPATH, f"{meta_xpath}//p[contains(., 'Progresso: 1 / 2')]"), "Progresso: 1 / 2")(driver),
             "Texto 'Progresso: 1 / 2' não encontrado após o primeiro clique."
        )
        print("Progresso 1/2 marcado.")
        time.sleep(1.5)

        self.wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()

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
        
    
    def test_resumo_semanal_cenario_3_novo_usuario(self):
        print("Iniciando: test_resumo_semanal_cenario_3 (Novo Usuário)")
        driver = self.driver
        
        driver.find_element(By.PARTIAL_LINK_TEXT, "Resumo Semanal").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Resumo Semanal"))
        print("Navegou para a página de Resumo.")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, 'body').text
        # (views.py: if not primeiro_checkin: ...)
        self.assertIn("Seu resumo semanal aparecerá aqui!", body_text)
        print("Verificado: Mensagem de 'Bem-vindo' (Cenário 3) exibida.")
        time.sleep(1)

    def test_resumo_semanal_cenario_2_sem_atividade(self):
        print("Iniciando: test_resumo_semanal_cenario_2 (Sem Atividade)")
        driver = self.driver

        oito_dias_atras = timezone.localdate() - timedelta(days=8)
        CheckIn.objects.create(usuario=self.user, data_checkin=oito_dias_atras)
        CheckIn.objects.filter(usuario=self.user).update(data_checkin=oito_dias_atras)
        print("Usuário 'envelhecido' 8 dias.")

        driver.find_element(By.PARTIAL_LINK_TEXT, "Resumo Semanal").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Resumo Semanal"))
        print("Navegou para a página de Resumo.")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Nenhuma novidade nesta semana", body_text)
        print("Verificado: Mensagem 'Nenhuma novidade' (Cenário 2) exibida.")
        time.sleep(1)

    def test_resumo_semanal_cenario_1_com_atividade(self):
        print("Iniciando: test_resumo_semanal_cenario_1 (Com Atividade)")
        driver = self.driver
        
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
        
        # (resumo_semanal.html: <h2>...Maior interesse de leitura...</h2>)
        self.assertIn("Maior interesse de leitura", body_text)
        self.assertIn("Astronomia — 3 leituras", body_text)
        
        self.assertIn("Anotações da Semana", body_text)
        self.assertIn("Minha anotação da semana", body_text)
        
        print("Verificado: Todas as atividades (Cenário 1) exibidas.")
        time.sleep(2)

    # ===================================================================
    # ★ NOVOS TESTES: HISTÓRIA 1 (FILTRO DE TEMAS) ★
    # ===================================================================

    def test_filtro_temas_cenario_3_erro_vazio(self):
        """
        Testa o Cenário 3: Salvar sem marcar nenhuma categoria.
        """
        print("Iniciando: test_filtro_temas_cenario_3 (Erro Vazio)")
        driver = self.driver
        
        # 1. Cria Categorias no banco para o teste
        Categoria.objects.create(nome="Esportes")
        Categoria.objects.create(nome="Tecnologia")
        
        # 2. Remove a categoria "Geral" que foi adicionada no setUp
        self.user.userprofile.categorias_seguidas.clear()
        
        # 3. Navega para a Home, que DEVE redirecionar
        driver.get(self.live_server_url + '/')
        
        # 4. Espera pelo redirect para a página de gerenciamento de temas
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Opções de Temas"))
        print("Navegou para a página de Temas (via redirect da home).")
        self.assertIn("Bem-vindo! Por favor, escolha seus temas", driver.find_element(By.TAG_NAME, 'body').text)
        
        # 5. Clica em "Salvar" sem marcar nada
        # (gerenciar_temas.html: <button ...>Salvar e ver Dashboard</button>)
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar e ver Dashboard')]").click()
        
        # 6. Verifica a mensagem de erro (Cenário 3)
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-red-100'), "Você precisa seguir ao menos uma categoria para salvar."))
        print("Verificado: Mensagem de erro 'precisa seguir ao menos uma' apareceu.")
        
        # 7. Verifica se permaneceu na página
        self.assertTrue(driver.current_url.endswith('/opcoes-de-temas/'))
        print("Verificado: Permaneceu na página de temas.")
        time.sleep(1)

    def test_filtro_temas_cenarios_1_e_2_salvar_e_alterar(self):
        """
        Testa os Cenários 1 e 2: Salvar e alterar filtros do Dashboard.
        """
        print("Iniciando: test_filtro_temas_cenarios_1_e_2 (Salvar e Alterar)")
        driver = self.driver
        
        # 1. Cria dados de teste
        # (A categoria "Geral" já existe do setUp)
        cat_esportes = Categoria.objects.create(nome="Esportes")
        cat_tech = Categoria.objects.create(nome="Tecnologia")
        cat_mito = Categoria.objects.create(nome="Mitologia")
        
        # Cria notícias para cada categoria
        Noticia.objects.create(titulo="Notícia de Esporte 1", categoria=cat_esportes)
        Noticia.objects.create(titulo="Notícia de Tecnologia 1", categoria=cat_tech)
        Noticia.objects.create(titulo="Notícia de Mitologia 1", categoria=cat_mito)
        
        # 2. (CENÁRIO 1) Navega para a página de Temas (pelo link na home)
        # (home.html: <a href="{% url 'gerenciar_temas' %}" ...>⚙️ Alterar Temas</a>)
        driver.find_element(By.PARTIAL_LINK_TEXT, "Alterar Temas").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Opções de Temas"))
        print("Navegou para a página de Temas (pelo link da Home).")
        
        # 3. Desmarca "Geral", Marca "Esportes" e "Tecnologia"
        driver.find_element(By.CSS_SELECTOR, f"input[value='{self.user.userprofile.categorias_seguidas.first().id}']").click() # Desmarca Geral
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_esportes.id}']").click()
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_tech.id}']").click()
        time.sleep(0.5)
        
        # 4. Clica em Salvar
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar e ver Dashboard')]").click()
        
        # 5. Verifica o Dashboard (Cenário 1)
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h2'), "Dashboard - MeuJornal"))
        print("Navegou para a Home (Dashboard) com filtros salvos.")
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Notícia de Esporte 1", body_text)
        self.assertIn("Notícia de Tecnologia 1", body_text)
        self.assertNotIn("Notícia de Mitologia 1", body_text)
        print("Verificado (Cenário 1): Apenas Esportes e Tecnologia aparecem.")
        time.sleep(1)

        # 6. (CENÁRIO 2) Volta para 'gerenciar_temas' (pelo link na home)
        driver.find_element(By.PARTIAL_LINK_TEXT, "Alterar Temas").click()
        self.wait.until(EC.text_to_be_present_in_element(self.MAIN_H1_SELECTOR, "Opções de Temas"))
        
        # 7. Desmarca "Esportes" e marca "Mitologia"
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_esportes.id}']").click() # Desmarca
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_mito.id}']").click() # Marca
        time.sleep(0.5)
        
        # 8. Clica em Salvar
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar e ver Dashboard')]").click()
        
        # 9. Verifica o Dashboard (Cenário 2)
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'h2'), "Dashboard - MeuJornal"))
        print("Navegou de volta à Home (Dashboard) com filtros alterados.")
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn("Notícia de Esporte 1", body_text)
        self.assertIn("Notícia de Tecnologia 1", body_text) # Continua marcado
        self.assertIn("Notícia de Mitologia 1", body_text) # Novo
        print("Verificado (Cenário 2): Apenas Tecnologia e Mitologia aparecem.")
        time.sleep(1)


    # ===================================================================
    # ★ NOVOS TESTES: HISTÓRIA 4 (CALENDÁRIO) ★
    # ===================================================================

def test_calendario_cenarios_1_2_3(self):
        """
        Testa os Cenários 1, 2 e 3 do Calendário de Leitura.
        """
        print("Iniciando: test_calendario_cenarios_1_2_3")
        driver = self.driver
        hoje = timezone.localdate()
        
        # 1. (CENÁRIO 3 - Usuário Novo)
        
        # 2. Navega para o Calendário
        driver.find_element(By.PARTIAL_LINK_TEXT, "Calendário").click()
        
        # --- ★ CORREÇÃO (H1 -> H2) ★ ---
        # (calendario.html usa <h2> para o título, não <h1>)
        calendario_h2_selector = (By.CSS_SELECTOR, "main h2")
        self.wait.until(EC.text_to_be_present_in_element(calendario_h2_selector, "Calendário de Leitura"))
        print("Navegou para a página de Calendário (Usuário Novo).")
        
        # 3. Verifica o dia atual (Azul)
        dia_azul = driver.find_element(By.XPATH, f"//div[contains(@class, 'bg-blue-600') and contains(., '{hoje.day}')]")
        self.assertTrue(dia_azul.is_displayed())
        print("Verificado (Cenário 3): Dia atual está Azul.")
        time.sleep(1)

        # 4. (CENÁRIOS 1 e 2 - Preparação)
        dia_anterior = hoje - timedelta(days=1)
        dois_dias_atras = hoje - timedelta(days=2)
        
        CheckIn.objects.filter(usuario=self.user).delete() # Limpa checkins
        CheckIn.objects.create(usuario=self.user, data_checkin=dois_dias_atras)
        DiarioEntry.objects.create(usuario=self.user, texto="Anotação de dois dias atrás", data_criacao=dois_dias_atras)
        print("Dados de teste (Check-in Verde, Dia Cinza, Anotação) criados.")

        # 5. Recarrega a página do calendário para ver os dados
        driver.refresh()
        
        # --- ★ CORREÇÃO (H1 -> H2) ★ ---
        self.wait.until(EC.text_to_be_present_in_element(calendario_h2_selector, "Calendário de Leitura"))
        print("Página recarregada com dados.")

        # 6. VERIFICA O CALENDÁRIO (CENÁRIO 1)
        
        # Dia Verde (Check-in)
        dia_verde = driver.find_element(By.XPATH, f"//div[contains(@class, 'bg-green-500') and contains(., '{dois_dias_atras.day}')]")
        self.assertTrue(dia_verde.is_displayed())
        print("Verificado (Cenário 1): Dia com check-in está Verde.")
        
        # Dia Cinza (Intervalo - Cenário 2)
        dia_cinza = driver.find_element(By.XPATH, f"//div[contains(@class, 'bg-gray-200') and contains(., '{dia_anterior.day}')]")
        self.assertTrue(dia_cinza.is_displayed())
        print("Verificado (Cenário 2): Dia sem check-in (intervalo) está Cinza.")
        
        # Dia com Anotação (★)
        anotacao_star = dia_verde.find_element(By.XPATH, ".//span[@title='Anotação no diário']")
        self.assertTrue(anotacao_star.is_displayed())
        self.assertIn("★", anotacao_star.text)
        print("Verificado (Cenário 1): Dia com anotação exibe ★.")
        
        print("Teste de fluxo (Calendário) concluído!")
        time.sleep(2)