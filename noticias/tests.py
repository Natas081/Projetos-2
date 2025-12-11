import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

from .models import Noticia, Interest, DiarioEntry, CheckIn, Goal, Categoria, UserProfile
from datetime import date, timedelta
from django.utils import timezone

class TestInterfaceUsuario(StaticLiveServerTestCase):
    
    DASHBOARD_H2 = (By.XPATH, "//h2[contains(text(), 'Dashboard - MeuJornal')]")

    @classmethod
    def setUpClass(cls):
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
        super().setUp()
        self.username = 'usuarioteste'
        self.password = 'senha1234'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

        cat_padrao = Categoria.objects.create(nome="Geral")
        self.user.userprofile.categorias_seguidas.add(cat_padrao)

        self.driver.get(f'{self.live_server_url}/login/')
        self.wait.until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(self.username)
        time.sleep(0.5)
        self.driver.find_element(By.NAME, 'password').send_keys(self.password)
        time.sleep(0.5)
        
        try:
            self.driver.find_element(By.XPATH, "//button[contains(., 'Entrar')]").click()
        except:
            self.driver.find_element(By.CSS_SELECTOR, ".form-container.sign-in form button").click()
        
        self.wait.until(EC.presence_of_element_located(self.DASHBOARD_H2))
        print(f"\nSetup: Usuário '{self.username}' logado e pronto para o teste.")
        time.sleep(1)

    def abrir_menu_navegar(self, link_text_partial):
        """
        Abre o menu lateral (que agora é oculto) e clica no link desejado.
        """
        driver = self.driver
        try:
            menu_btn = driver.find_element(By.ID, "menuBtn")
            if menu_btn.is_displayed():
                menu_btn.click()
                time.sleep(0.5)
        except:
            pass 
        
        link = self.wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, link_text_partial)))
        link.click()

    
    
    

    def test_fluxo_interesses_e_rotina(self):
        print("Iniciando: test_fluxo_interesses_e_rotina")
        driver = self.driver
        
        self.abrir_menu_navegar("Interesses")
        
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Seus Interesses"))
        time.sleep(1)

        nome_interesse = "Testes Automatizados"
        driver.find_element(By.NAME, 'name').send_keys(nome_interesse)
        time.sleep(0.5)
        driver.find_element(By.NAME, 'target_frequency').send_keys("2")
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//button[contains(., 'Adicionar')]").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Interesse \"Testes Automatizados\" adicionado!"))
        time.sleep(1)
        
        self.abrir_menu_navegar("Rotina")
        
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Rotina Semanal"))
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
        
        try:
            widget = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fixed")))
            self.assertIn("0 dia(s)", widget.text)
            widget.find_element(By.TAG_NAME, 'a').click()
        except:
             driver.get(f'{self.live_server_url}/streak/')

        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Seu Streak de Leitura"))
        time.sleep(1)

        checkin_button = driver.find_element(By.XPATH, "//button[contains(., 'Confirmar acesso de hoje')]")
        checkin_button.click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Check-in diário confirmado!"))
        print("Verificado: Mensagem de check-in OK.")
        
        xpath_confirmacao_streak = "//p[contains(@class, 'text-green-600') and contains(text(), 'Você já confirmou o acesso hoje')]"
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_confirmacao_streak)))
        
        streak_text = driver.find_element(By.CSS_SELECTOR, 'span.text-4xl').text
        self.assertIn("1", streak_text)
        print("Verificado: Contagem de streak na página é 1.")
        print("Teste de fluxo (Streak) concluído!")
        time.sleep(2)


    def test_fluxo_diario_completo(self):
        print("Iniciando: test_fluxo_diario_completo")
        driver = self.driver
        
        self.abrir_menu_navegar("Diário")
        
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Diário do Aprendizado"))
        
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
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Editar Anotação"))
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
        
        time.sleep(1) 
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-green-100'), "Anotação removida com sucesso!"))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Nenhuma anotação ainda"))
        self.assertNotIn(texto_editado, driver.find_element(By.TAG_NAME, 'body').text)
        print("Verificado: Anotação excluída com sucesso.")
        print("Teste de fluxo (Diário) concluído!")
        time.sleep(2)
        
    
    def test_resumo_semanal_cenario_3_novo_usuario(self):
        print("Iniciando: test_resumo_semanal_cenario_3 (Novo Usuário)")
        driver = self.driver
        
        self.abrir_menu_navegar("Resumo Semanal")
        
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Resumo Semanal"))
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Seu resumo semanal aparecerá aqui!", body_text)
        print("Verificado: Mensagem de 'Bem-vindo' (Cenário 3) exibida.")
        time.sleep(1)

    def test_resumo_semanal_cenario_2_sem_atividade(self):
        print("Iniciando: test_resumo_semanal_cenario_2 (Sem Atividade)")
        driver = self.driver

        oito_dias_atras = timezone.localdate() - timedelta(days=8)
        CheckIn.objects.create(usuario=self.user, data_checkin=oito_dias_atras)
        CheckIn.objects.filter(usuario=self.user).update(data_checkin=oito_dias_atras)
        
        self.abrir_menu_navegar("Resumo Semanal")

        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Resumo Semanal"))
        
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

        self.abrir_menu_navegar("Resumo Semanal")

        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Resumo Semanal"))
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Novos Interesses", body_text)
        self.assertIn("Astronomia", body_text)
        self.assertIn("Maior interesse de leitura", body_text)
        self.assertIn("Astronomia — 3 leituras", body_text)
        self.assertIn("Anotações da Semana", body_text)
        print("Verificado: Todas as atividades (Cenário 1) exibidas.")
        time.sleep(2)

    
    
    

    def test_filtro_temas_cenario_3_erro_vazio(self):
        print("Iniciando: test_filtro_temas_cenario_3 (Erro Vazio)")
        driver = self.driver
        
        Categoria.objects.create(nome="Esportes")
        Categoria.objects.create(nome="Tecnologia")
        
        self.user.userprofile.categorias_seguidas.clear()
        
        driver.get(self.live_server_url + '/opcoes-de-temas/')
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Opções de Temas"))
        print("Navegou para a página de Temas.")
        
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar e ver Dashboard')]").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'bg-red-100'), "Você precisa seguir ao menos uma categoria para salvar."))
        print("Verificado: Mensagem de erro 'precisa seguir ao menos uma' apareceu.")
        
        self.assertTrue(driver.current_url.endswith('/opcoes-de-temas/'))
        print("Verificado: Permaneceu na página de temas.")
        time.sleep(1)

    def test_filtro_temas_cenarios_1_e_2_salvar_e_alterar(self):
        print("Iniciando: test_filtro_temas_cenarios_1_e_2 (Salvar e Alterar)")
        driver = self.driver
        
        cat_esportes = Categoria.objects.create(nome="Esportes")
        cat_tech = Categoria.objects.create(nome="Tecnologia")
        cat_mito = Categoria.objects.create(nome="Mitologia")
        
        Noticia.objects.create(titulo="Notícia de Esporte 1", categoria=cat_esportes)
        Noticia.objects.create(titulo="Notícia de Tecnologia 1", categoria=cat_tech)
        Noticia.objects.create(titulo="Notícia de Mitologia 1", categoria=cat_mito)
        
        driver.find_element(By.PARTIAL_LINK_TEXT, "Alterar Temas").click()
        
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Opções de Temas"))
        print("Navegou para a página de Temas.")
        
        id_geral = self.user.userprofile.categorias_seguidas.first().id
        driver.find_element(By.CSS_SELECTOR, f"input[value='{id_geral}']").click()
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_esportes.id}']").click()
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_tech.id}']").click()
        
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar e ver Dashboard')]").click()
        
        self.wait.until(EC.presence_of_element_located(self.DASHBOARD_H2))
        print("Navegou para a Home (Dashboard) com filtros salvos.")
        
        grid_noticias = driver.find_element(By.CSS_SELECTOR, "div.mt-12 div.grid").text
        
        self.assertIn("Notícia de Esporte 1", grid_noticias)
        self.assertIn("Notícia de Tecnologia 1", grid_noticias)
        self.assertNotIn("Notícia de Mitologia 1", grid_noticias)
        print("Verificado (Cenário 1): Apenas Esportes e Tecnologia aparecem no feed.")
        time.sleep(1)

        driver.get(self.live_server_url + '/opcoes-de-temas/') 
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Opções de Temas"))
        
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_esportes.id}']").click() 
        driver.find_element(By.CSS_SELECTOR, f"input[value='{cat_mito.id}']").click() 
        time.sleep(0.5)
        
        driver.find_element(By.XPATH, "//button[contains(., 'Salvar e ver Dashboard')]").click()
        
        self.wait.until(EC.presence_of_element_located(self.DASHBOARD_H2))
        print("Navegou de volta à Home (Dashboard) com filtros alterados.")
        
        grid_noticias = driver.find_element(By.CSS_SELECTOR, "div.mt-12 div.grid").text
        self.assertNotIn("Notícia de Esporte 1", grid_noticias)
        self.assertIn("Notícia de Tecnologia 1", grid_noticias)
        self.assertIn("Notícia de Mitologia 1", grid_noticias)
        print("Verificado (Cenário 2): Apenas Tecnologia e Mitologia aparecem no feed.")
        time.sleep(1)


    
    
    

    def test_calendario_cenarios_1_2_3(self):
        print("Iniciando: test_calendario_cenarios_1_2_3")
        driver = self.driver
        hoje = timezone.localdate()
        
        self.abrir_menu_navegar("Calendário")
        
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Calendário de Leitura')]")))
        print("Navegou para a página de Calendário.")
        
        dia_azul = driver.find_element(By.XPATH, f"//div[contains(@class, 'bg-blue-600')]//span[text()='{hoje.day}']")
        self.assertTrue(dia_azul.is_displayed())
        print("Verificado (Cenário 3): Dia atual está Azul.")
        time.sleep(1)

        dia_teste = 1
        if hoje.day == 1:
            dia_teste = 2
            
        data_teste = date(hoje.year, hoje.month, dia_teste)
        
        CheckIn.objects.filter(usuario=self.user).delete()
        DiarioEntry.objects.filter(usuario=self.user).delete()
        
        ck = CheckIn.objects.create(usuario=self.user) 
        CheckIn.objects.filter(pk=ck.pk).update(data_checkin=data_teste)

        anotacao = DiarioEntry.objects.create(usuario=self.user, texto="Anotação teste")
        DiarioEntry.objects.filter(pk=anotacao.pk).update(data_criacao=data_teste)
        
        print(f"Dados de teste criados e forçados para o dia {dia_teste}.")

        url_calendario = f"{self.live_server_url}/routine/calendario/"
        driver.get(url_calendario)
        
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Calendário de Leitura')]")))
        print("Página recarregada com dados.")

        xpath_verde = f"//div[contains(@class, 'bg-green-500')]//span[text()='{dia_teste}']"
        dia_verde_elem = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_verde)))
        self.assertTrue(dia_verde_elem.is_displayed())
        print(f"Verificado (Cenário 1): Dia {dia_teste} com check-in está Verde.")
        
        dia_verde_div = dia_verde_elem.find_element(By.XPATH, "./..")
        anotacao_star = dia_verde_div.find_element(By.XPATH, ".//span[@title='Anotação no diário']")
        self.assertTrue(anotacao_star.is_displayed())
        print("Verificado (Cenário 1): Dia com anotação exibe ★.")
        
        print("Teste de fluxo (Calendário) concluído!")
        time.sleep(2)

    
    
    

    def test_sugestao_dia_cenario_2_sem_noticias(self):
        print("Iniciando: test_sugestao_dia_cenario_2 (Sem Notícias)")
        driver = self.driver
        
        Noticia.objects.all().delete()
        self.user.userprofile.sugestao_do_dia = None
        self.user.userprofile.save()

        driver.get(f'{self.live_server_url}/')
        self.wait.until(EC.presence_of_element_located(self.DASHBOARD_H2))

        body_text = driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn("Nenhuma notícia cadastrada no sistema para sugerir hoje.", body_text)
        print("Verificado (Cenário 2): Mensagem de erro exibida corretamente.")
        time.sleep(1)


    def test_sugestao_dia_cenarios_1_e_3_com_noticias_e_persistencia(self):
        print("Iniciando: test_sugestao_dia_cenarios_1_e_3 (Com Notícias e Persistência)")
        driver = self.driver

        n1 = Noticia.objects.create(titulo="Notícia Incrível A", categoria=Categoria.objects.create(nome="Tema A"))
        n2 = Noticia.objects.create(titulo="Notícia Fantástica B", categoria=Categoria.objects.create(nome="Tema B"))

        self.user.userprofile.sugestao_do_dia = None
        self.user.userprofile.sugestao_data = None
        self.user.userprofile.save()

        driver.refresh()
        self.wait.until(EC.presence_of_element_located(self.DASHBOARD_H2))
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        
        
        encontrou_sugestao = "Notícia Incrível A" in body_text or "Notícia Fantástica B" in body_text
        self.assertTrue(encontrou_sugestao, "Nenhuma sugestão apareceu na Home.")
        print("Teste de sugestão: Sugestão encontrada na Home.")