from git import Repo
from datetime import datetime
import os
from git import Git
import getpass
from urllib.parse import urlparse

def extract_repo_name(repo_url):
    """
    Extrai o nome do repositório da URL do GitHub.
    
    Args:
        repo_url (str): URL do repositório GitHub
    
    Returns:
        str: Nome do repositório
    """
    # Remove .git do final se existir
    repo_url = repo_url.rstrip('.git')
    
    # Parse da URL
    parsed_url = urlparse(repo_url)
    
    # Pega o último elemento do path
    path_parts = parsed_url.path.strip('/').split('/')
    repo_name = path_parts[-1]
    
    return repo_name

def validate_github_url(url):
    """
    Valida se a URL fornecida é uma URL válida do GitHub.
    
    Args:
        url (str): URL para validar
    
    Returns:
        bool: True se for válida, False caso contrário
    """
    try:
        parsed = urlparse(url)
        return all([
            parsed.scheme in ('http', 'https'),
            'github.com' in parsed.netloc,
            len(parsed.path.strip('/').split('/')) >= 2
        ])
    except:
        return False

def clone_or_pull_repo(repo_url, local_path, username=None, token=None):
    """
    Clona ou atualiza o repositório local usando autenticação.
    
    Args:
        repo_url (str): URL do repositório GitHub
        local_path (str): Caminho local onde o repositório será clonado
        username (str): Nome de usuário do GitHub
        token (str): Token de acesso pessoal do GitHub
    """
    # Formata a URL com autenticação
    if token:
        auth_url = f'https://{token}@github.com/{repo_url.split("github.com/")[1]}'
    elif username:
        password = getpass.getpass("Digite sua senha do GitHub: ")
        auth_url = f'https://{username}:{password}@github.com/{repo_url.split("github.com/")[1]}'
    
    try:
        if os.path.exists(local_path):
            # Se o repositório já existe, apenas atualiza
            repo = Repo(local_path)
            origin = repo.remotes.origin
            origin.pull()
            print("Repositório atualizado com sucesso!")
        else:
            # Se não existe, clona o repositório
            Repo.clone_from(auth_url, local_path)
            print("Repositório clonado com sucesso!")
        
        return True
    except Exception as e:
        print(f"Erro ao clonar/atualizar repositório: {str(e)}")
        return False

def listar_commits_branch(repo_path, branch_name='dev', output_file='reports/commits_log.txt'):
    """
    Lista todos os commits de uma branch específica e salva em um arquivo.
    
    Args:
        repo_path (str): Caminho local do repositório
        branch_name (str): Nome da branch (default: 'dev')
        output_file (str): Nome do arquivo de saída (default: 'reports/commits_log.txt')
    """
    try:
        # Abre o repositório
        repo = Repo(repo_path)
        
        # Certifica-se de estar na branch correta
        repo.git.checkout(branch_name)
        
        # Prepara o cabeçalho
        header = f"\nListagem de commits da branch {branch_name}\n"
        separator = "=" * 50
        
        # Lista para armazenar as linhas
        output_lines = [header, separator + "\n"]
        
        print(header)
        print(separator)
        
        # Lista os commits
        for commit in repo.iter_commits(branch_name):
            data = datetime.fromtimestamp(commit.committed_date)
            
            commit_info = [
                f"Commit: {commit.hexsha}",
                f"Autor: {commit.author}",
                f"Data: {data.strftime('%d/%m/%Y %H:%M:%S')}",
                f"Mensagem: {commit.message.strip()}",
                "-" * 50 + "\n"
            ]
            
            for line in commit_info:
                print(line)
                output_lines.append(line + "\n")
        
        # Salva no arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        
        print(f"\nLog de commits salvo em: {os.path.abspath(output_file)}")
            
    except Exception as e:
        error_msg = f"Erro ao acessar o repositório: {str(e)}"
        print(error_msg)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_msg)

def main():
    # Solicita a URL do repositório
    while True:
        repo_url = input("\nDigite a URL do repositório GitHub: ").strip()
        if validate_github_url(repo_url):
            break
        print("URL inválida! Por favor, forneça uma URL válida do GitHub (ex: https://github.com/usuario/repositorio)")
    
    # Extrai o nome do repositório para usar no arquivo de log
    repo_name = extract_repo_name(repo_url)
    
    # Configura os caminhos
    local_path = f"./repositories/{repo_name}"  # Diretório local onde o repo será clonado
    branch_name = "dev"
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"reports/commits_log_{repo_name}_{current_date}.txt"
    
    # Solicita informações de autenticação
    print("\nEscolha o método de autenticação:")
    print("1. Token de acesso pessoal (Recomendado)")
    print("2. Usuário e senha")
    
    while True:
        choice = input("Escolha (1 ou 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Opção inválida! Por favor, escolha 1 ou 2.")
    
    if choice == "1":
        token = getpass.getpass("Digite seu token de acesso pessoal do GitHub: ")
        success = clone_or_pull_repo(repo_url, local_path, token=token)
    else:
        username = input("Digite seu nome de usuário do GitHub: ")
        success = clone_or_pull_repo(repo_url, local_path, username=username)
    
    if success:
        listar_commits_branch(local_path, branch_name, output_file)

if __name__ == "__main__":
    main()