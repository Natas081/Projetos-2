from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, timedelta # Importe date e timedelta

# --- SEUS MODELOS EXISTENTES ---

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    leitura_streak = models.IntegerField(default=0, verbose_name="Sequência de Leitura")

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

# --- FIM DOS SEUS MODELOS EXISTENTES ---


# --- NOVOS MODELOS (OU MODELOS QUE VOCÊ JÁ DEVE TER) ---
# Você PRECISA de um modelo de Interesses para sua história de usuário
class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('user', 'name') # Um usuário não pode ter o mesmo interesse duas vezes

    def __str__(self):
        return f'{self.name} (de {self.user.username})'

# Você PRECISA de um modelo de Notícia que se relacione a um Interesse
class Noticia(models.Model):
    # (Seus campos de notícia: titulo, link, pubDate, etc...)
    titulo = models.CharField(max_length=255)
    link = models.URLField()
    # ...
    
    # Esta é a ligação crucial:
    interest = models.ForeignKey(Interest, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo


# --- NOVO MODELO DA SUA HISTÓRIA DE USUÁRIO ---
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name='goals')
    targetFrequency = models.PositiveIntegerField() # O "X vezes por semana"
    currentProgress = models.PositiveIntegerField(default=0) # O contador
    weekStartDate = models.DateField() # Data de início da semana para resetar

    class Meta:
        # Garante que um usuário só pode ter uma meta por interesse por semana
        unique_together = ('user', 'interest', 'weekStartDate')

    def __str__(self):
        return f"{self.user.username} - {self.interest.name}: {self.currentProgress}/{self.targetFrequency}"

    @staticmethod
    def get_start_of_week():
        """Retorna o Domingo (ou Segunda) da semana atual."""
        today = date.today()
        # weekday() é 0-6 (Seg-Dom). 
        # (today.weekday() + 1) % 7 -> Transforma Domingo em 0.
        # Ajuste se sua semana começar na Segunda (só usar today.weekday())
        start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
        return start_of_week