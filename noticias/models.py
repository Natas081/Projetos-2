# Em noticias/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, timedelta

# -------------------------
# CATEGORIAS (TEMAS GLOBAIS)
# -------------------------
class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Esportes, Tecnologia")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome


# -------------------------
# PERFIL DO USUÁRIO (STREAK)
# -------------------------
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    leitura_streak = models.PositiveIntegerField(default=0, verbose_name="Sequência de Leitura")
    ultimo_checkin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.usuario.username} - Streak: {self.leitura_streak}'


# -------------------------
# PERFIL ADICIONAL (UserProfile OFICIAL)
# -------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField("Nome de exibição", max_length=80, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Categorias seguidas pelo usuário
    categorias_seguidas = models.ManyToManyField(Categoria, blank=True, related_name="seguidores")

    # -------------------------
    # SUGESTÃO DE LEITURA DO DIA
    # -------------------------
    sugestao_do_dia = models.ForeignKey(
        "Noticia",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sugestoes_do_dia"
    )
    sugestao_data = models.DateField(null=True, blank=True)

    def get_ou_gerar_sugestao_do_dia(self):
        """
        Encapsula a lógica da Sugestão do Dia.
        [MODIFICADO] Agora sugere qualquer notícia, independente dos interesses.
        Retorna uma tupla: (sugestao_obj, mensagem_str)
        """
        today = date.today()
        
        # 1. (ALTERAÇÃO) O bloco do "Cenário 2" foi REMOVIDO.
        #    Não verificamos mais se o utilizador tem 'temas_salvos'.

        # Cenário 3: Sugestão já foi gerada hoje (Esta é a primeira verificação agora)
        if self.sugestao_do_dia and self.sugestao_data == today:
            # Retorna a sugestão já salva
            return (self.sugestao_do_dia, None) 

        # Cenário 1 (Modificado): Gerar nova sugestão de QUALQUER tema
        
        # 2. (ALTERAÇÃO) A consulta agora usa .all() para pegar qualquer notícia,
        #    em vez de .filter(categoria__in=temas_salvos)
        nova_sugestao = Noticia.objects.all().order_by('?').first()

        if nova_sugestao:
            # Encontramos uma. Salva no perfil.
            self.sugestao_do_dia = nova_sugestao
            self.sugestao_data = today
            self.save()
            return (nova_sugestao, None)
        else:
            # 3. (ALTERAÇÃO) A mensagem de fallback mudou.
            #    Isto agora significa que não há NENHUMA notícia no banco.
            self.sugestao_do_dia = None
            self.sugestao_data = None
            self.save()
            return (None, "Nenhuma notícia cadastrada no sistema para sugerir hoje.")

    def __str__(self):
        return f"Perfil de {self.user.username}"


# Criar perfil automaticamente
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
        UserProfile.objects.create(user=instance)
    else:
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(usuario=instance)
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)


# -------------------------
# CHECK-IN DIÁRIO
# -------------------------
class CheckIn(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_checkin = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'data_checkin')
        verbose_name = "Check-in Diário"
        verbose_name_plural = "Check-ins Diários"

    def __str__(self):
        return f'Check-in de {self.usuario.username} em {self.data_checkin.strftime("%d/%m/%Y")}'


# -------------------------
# INTERESSES
# -------------------------
class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.name} (de {self.user.username})'


# -------------------------
# NOTÍCIAS
# -------------------------
class Noticia(models.Model):
    titulo = models.CharField(max_length=255)
    link = models.URLField()
    resumo = models.TextField(blank=True, null=True)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="noticias"
    )

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo


# -------------------------
# METAS DE LEITURA
# -------------------------
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name='goals')
    targetFrequency = models.PositiveIntegerField()
    currentProgress = models.PositiveIntegerField(default=0)
    weekStartDate = models.DateField()

    class Meta:
        unique_together = ('user', 'interest', 'weekStartDate')

    def __str__(self):
        return f"{self.user.username} - {self.interest.name}: {self.currentProgress}/{self.targetFrequency}"

    @staticmethod
    def get_start_of_week():
        today = date.today()
        return today - timedelta(days=today.weekday())


# -------------------------
# DIÁRIO DO APRENDIZADO
# -------------------------
class DiarioEntry(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Anotação do Diário"
        verbose_name_plural = "Anotações do Diário"

    def __str__(self):
        return f'{self.usuario.username} - {self.data_criacao.strftime("%d/%m/%Y %H:%M")}'
