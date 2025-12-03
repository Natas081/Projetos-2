# Guia de Contribuição - MeuJornal 📰

Obrigado pelo interesse em contribuir com o **MeuJornal**\! Este documento estabelece as diretrizes para garantir que o desenvolvimento flua bem entre a equipe e que a qualidade do código seja mantida.

## 🚀 Como Configurar o Ambiente

Para começar a desenvolver, siga estes passos:

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/SEU-USUARIO/Projetos-2.git
    cd Projetos-2
    ```

2.  **Crie e ative o ambiente virtual (.venv):**

    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # Linux/Mac
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

    *(Nota: Isso instalará Django, Pillow, Selenium, etc.)*

4.  **Configure o Banco de Dados:**

    ```bash
    python manage.py migrate
    ```

5.  **Rode o servidor local:**

    ```bash
    python manage.py runserver
    ```

-----

## ✅ Testes Automatizados (Obrigatório)

Nós utilizamos **Selenium** para testes End-to-End (E2E). Antes de enviar qualquer código, você **deve** garantir que todos os testes passem.

### Como rodar os testes:

No terminal, com o ambiente virtual ativo:

```bash
python manage.py test
```

> **Atenção:** O CI/CD (GitHub Actions) rodará esses testes automaticamente. Se algum teste falhar, o deploy no Render **não será realizado**. Não quebre o build\! 🛡️

-----

## 🌳 Fluxo de Trabalho Git (Workflow)

Para manter o histórico organizado e evitar conflitos:

1.  **Nunca comite direto na `main`**: Sempre crie uma branch para sua tarefa.

    ```bash
    git checkout -b feature/nome-da-historia
    # ou
    git checkout -b fix/arrumando-bug
    ```

2.  **Mantenha sua branch atualizada**: Antes de começar, puxe as últimas mudanças.

    ```bash
    git checkout main
    git pull
    git checkout suabranch
    git merge main
    ```

3.  **Commits Descritivos**: Escreva mensagens claras sobre o que foi feito.

      * ❌ Ruim: "ajustes", "arrumando codigo"
      * ✅ Bom: "Adiciona funcionalidade de calendário na rotina", "Corrige erro no teste do filtro de temas"

-----

## 📝 Padrões de Código

  * **HTML/Templates:** Use as classes do Tailwind CSS sempre que possível. Evite CSS inline (`style="..."`).
  * **Python:** Siga a PEP 8. Mantenha as views organizadas e use comentários se a lógica for complexa.
  * **Imagens:** Se precisar de imagens novas, coloque em `static/` e use a tag `{% static %}`.

-----

## 📦 Pull Requests (PR)

Quando terminar sua tarefa:

1.  Rode os testes (`python manage.py test`) uma última vez.
2.  Empurre sua branch: `git push origin feature/nome-da-sua-branch`.
3.  Abra um **Pull Request** no GitHub para a branch `main`.
4.  Verifique se a **Action do GitHub** ficou verde (✅).

-----

Bom código\! 🚀
