# Configuração do Ambiente

Este guia descreve como configurar o ambiente para executar o projeto. Siga os passos abaixo de acordo com o seu sistema operacional (**Windows** ou **Linux**).

---

## **1. Criar e Ativar o Ambiente Virtual**

### **No Windows**
1. Abra o terminal (ou **PowerShell**).
2. Navegue até o diretório raiz do projeto:
   ```bash
   cd caminho/para/o/projeto
   ```
3. Crie o ambiente virtual com o comando:
   ```bash
   python -m venv venv
   ```
4. Ative o ambiente virtual:
   ```bash
   venv\Scripts\activate
   ```

### **No Linux**
1. Abra o terminal.
2. Navegue até o diretório raiz do projeto:
   ```bash
   cd caminho/para/o/projeto
   ```
3. Crie o ambiente virtual com o comando:
   ```bash
   python3 -m venv venv
   ```
4. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```

---

## **2. Instalar Dependências**

Com o ambiente virtual ativado, instale os pacotes listados no arquivo `requirements.txt`:

### **No Windows e no Linux**
1. Certifique-se de que o ambiente virtual está ativado.
2. Execute o comando para instalar as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## **3. Verificar a Instalação**

Para garantir que as dependências foram instaladas corretamente, execute:
```bash
pip freeze
```
Isso exibirá uma lista dos pacotes instalados. Verifique se os pacotes correspondem ao `requirements.txt`.

---

## **4. Desativar o Ambiente Virtual**

Quando terminar, você pode desativar o ambiente virtual com o comando:
```bash
deactivate
```

---

Caso precise de mais informações ou enfrente problemas, consulte a documentação oficial do Python ou entre em contato com o administrador do projeto.

