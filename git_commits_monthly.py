from git import Repo
from datetime import datetime
import os
import getpass
from urllib.parse import urlparse
from collections import defaultdict
import calendar
from tabulate import tabulate
import matplotlib.pyplot as plt
from pathlib import Path

def validate_github_url(url):
    """
    Valida se a URL fornecida é uma URL válida do GitHub.
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

def extract_repo_name(repo_url):
    """
    Extrai o nome do repositório da URL do GitHub.
    """
    repo_url = repo_url.rstrip('.git')
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    return path_parts[-1]

def clone_or_pull_repo(repo_url, local_path, username=None, token=None):
    """
    Clona ou atualiza o repositório local usando autenticação.
    """
    if token:
        auth_url = f'https://{token}@github.com/{repo_url.split("github.com/")[1]}'
    elif username:
        password = getpass.getpass("Digite sua senha do GitHub: ")
        auth_url = f'https://{username}:{password}@github.com/{repo_url.split("github.com/")[1]}'
    
    try:
        if os.path.exists(local_path):
            repo = Repo(local_path)
            origin = repo.remotes.origin
            origin.pull()
            print("Repositório atualizado com sucesso!")
        else:
            Repo.clone_from(auth_url, local_path)
            print("Repositório clonado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao clonar/atualizar repositório: {str(e)}")
        return False

def analisar_commits_por_mes(repo_path, branch_name='dev'):
    """
    Analisa os commits por mês e gera estatísticas.
    """
    repo = Repo(repo_path)
    commits_por_mes = defaultdict(int)
    commits_por_autor = defaultdict(int)
    total_commits = 0
    
    # Dicionário para armazenar commits por autor por mês
    commits_autor_mes = defaultdict(lambda: defaultdict(int))
    
    for commit in repo.iter_commits(branch_name):
        data = datetime.fromtimestamp(commit.committed_date)
        mes_ano = data.strftime('%Y-%m')
        autor = commit.author.name
        
        commits_por_mes[mes_ano] += 1
        commits_por_autor[autor] += 1
        commits_autor_mes[mes_ano][autor] += 1
        total_commits += 1
    
    return {
        'commits_por_mes': dict(commits_por_mes),
        'commits_por_autor': dict(commits_por_autor),
        'commits_autor_mes': dict(commits_autor_mes),
        'total_commits': total_commits
    }

def criar_grafico(dados, repo_name, output_path):
    """
    Cria um gráfico de barras dos commits por mês.
    """
    commits_por_mes = dados['commits_por_mes']
    
    # Ordenar por mês
    meses_ordenados = sorted(commits_por_mes.keys())
    commits = [commits_por_mes[mes] for mes in meses_ordenados]
    
    # Criar labels mais legíveis (ex: "Jan 2024" em vez de "2024-01")
    labels = []
    for mes in meses_ordenados:
        ano, mes = mes.split('-')
        nome_mes = calendar.month_abbr[int(mes)]
        labels.append(f"{nome_mes} {ano}")
    
    plt.figure(figsize=(12, 6))
    plt.bar(labels, commits)
    plt.title(f'Commits por Mês - {repo_name}')
    plt.xlabel('Mês')
    plt.ylabel('Número de Commits')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Salvar o gráfico
    grafico_path = os.path.join(output_path, f'commits_mensal_{repo_name}.png')
    plt.savefig(grafico_path)
    plt.close()
    
    return grafico_path

def gerar_relatorio(dados, repo_name, output_path):
    """
    Gera um relatório detalhado em formato Markdown.
    """
    commits_por_mes = dados['commits_por_mes']
    commits_por_autor = dados['commits_por_autor']
    commits_autor_mes = dados['commits_autor_mes']
    total_commits = dados['total_commits']
    
    # Criar diretório para relatórios se não existir
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_file = os.path.join(output_path, f'relatorio_commits_{repo_name}_{timestamp}.md')
    
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write(f"# Relatório de Commits - {repo_name}\n\n")
        f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        # Resumo
        f.write("## Resumo\n\n")
        f.write(f"- Total de commits: {total_commits}\n")
        f.write(f"- Período analisado: {min(commits_por_mes.keys())} a {max(commits_por_mes.keys())}\n")
        f.write(f"- Total de contribuidores: {len(commits_por_autor)}\n\n")
        
        # Commits por mês
        f.write("## Commits por Mês\n\n")
        tabela_meses = []
        for mes in sorted(commits_por_mes.keys()):
            ano, num_mes = mes.split('-')
            nome_mes = calendar.month_name[int(num_mes)]
            tabela_meses.append([f"{nome_mes} {ano}", commits_por_mes[mes]])
        
        f.write(tabulate(tabela_meses, headers=['Mês', 'Commits'], tablefmt='pipe'))
        f.write("\n\n")
        
        # Commits por autor
        f.write("## Commits por Autor\n\n")
        tabela_autores = [[autor, commits] for autor, commits in 
                         sorted(commits_por_autor.items(), key=lambda x: x[1], reverse=True)]
        f.write(tabulate(tabela_autores, headers=['Autor', 'Commits'], tablefmt='pipe'))
        f.write("\n\n")
        
        # Detalhamento mensal por autor
        f.write("## Detalhamento Mensal por Autor\n\n")
        for mes in sorted(commits_autor_mes.keys()):
            ano, num_mes = mes.split('-')
            nome_mes = calendar.month_name[int(num_mes)]
            f.write(f"### {nome_mes} {ano}\n\n")
            
            tabela_mensal = [[autor, commits] for autor, commits in 
                            sorted(commits_autor_mes[mes].items(), key=lambda x: x[1], reverse=True)]
            f.write(tabulate(tabela_mensal, headers=['Autor', 'Commits'], tablefmt='pipe'))
            f.write("\n\n")
        
        # Referência ao gráfico
        f.write("## Gráfico de Commits\n\n")
        f.write(f"![Gráfico de commits por mês](commits_mensal_{repo_name}.png)\n")
    
    return relatorio_file

def main():
    # Solicita a URL do repositório
    while True:
        repo_url = input("\nDigite a URL do repositório GitHub: ").strip()
        if validate_github_url(repo_url):
            break
        print("URL inválida! Por favor, forneça uma URL válida do GitHub.")
    
    repo_name = extract_repo_name(repo_url)
    local_path = f"./repositories/{repo_name}"
    
    # Solicita autenticação
    print("\nEscolha o método de autenticação:")
    print("1. Token de acesso pessoal (Recomendado)")
    print("2. Usuário e senha")
    
    choice = input("Escolha (1 ou 2): ").strip()
    
    if choice == "1":
        token = getpass.getpass("Digite seu token de acesso pessoal do GitHub: ")
        success = clone_or_pull_repo(repo_url, local_path, token=token)
    else:
        username = input("Digite seu nome de usuário do GitHub: ")
        success = clone_or_pull_repo(repo_url, local_path, username=username)
    
    if success:
        print("\nAnalisando commits...")
        dados = analisar_commits_por_mes(local_path)
        
        # Criar diretório para relatórios
        output_path = './reports'
        Path(output_path).mkdir(exist_ok=True)
        
        # Gerar gráfico
        print("Gerando gráfico...")
        grafico_path = criar_grafico(dados, repo_name, output_path)
        
        # Gerar relatório
        print("Gerando relatório...")
        relatorio_path = gerar_relatorio(dados, repo_name, output_path)
        
        print(f"\nRelatório gerado com sucesso!")
        print(f"Relatório: {os.path.abspath(relatorio_path)}")
        print(f"Gráfico: {os.path.abspath(grafico_path)}")

if __name__ == "__main__":
    main()