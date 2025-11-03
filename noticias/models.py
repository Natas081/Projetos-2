from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, timedelta


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField("Nome de exibição", max_length=80, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    leitura_streak = models.IntegerField(default=0, verbose_name="Sequência de Leitura")
    ultima_leitura = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.usuario.username} - Streak: {self.leitura_streak}'


@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
    instance.perfil.save()


class CheckIn(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_checkin = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'data_checkin')
        verbose_name = "Check-in Diário"
        verbose_name_plural = "Check-ins Diários"

    def __str__(self):
        return f'Check-in de {self.usuario.username} em {self.data_checkin.strftime("%d/%m/%Y")}'


class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.name} (de {self.user.username})'


class Noticia(models.Model):
    titulo = models.CharField(max_length=255)
    link = models.URLField()
    resumo = models.TextField(blank=True, null=True)
    interest = models.ForeignKey(Interest, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo


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
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week


# -----------------------------------------
# ✅ MODELO DO DIÁRIO DO APRENDIZADO
# -----------------------------------------
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
