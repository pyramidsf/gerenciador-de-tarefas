# Gerenciador de Tarefas 
Sistema de gerenciamento de tarefas baseado em microserviços, focado em rápida iteração e hot-reload para desenvolvimento local.

## Tecnologias Utilizadas
- Conteinerização: Podman e Podman-compose.
- Proxy/Web Server: Nginx.
- Backend: Python FastAPI.
- Banco de Dados: PostgreSQL.
- Frontend: HTML5 + JavaScript. 

## Arquitetura do Projeto
O sistema roda isolado em uma rede interna do **Podman**.
1. Cliente (Browser) acessa localhost:8080.
2. **Nginx** serve arquivos estáticos (HTML) no app /.
3. **Ngnix** redireciona requisições /api/* para o container **Backend**.
4. **Backend** processa a lógica e persiste dados no container **Database**.

## Como Rodar 
1. Clone esse repositório e acesse o diretório do projeto (**app**). 
2. Construa e inicie os containers com o comando: 
```bash
   podman-compose up --build 
```
3. Cheque os containers que estão rodando
```bash
  podman ps
```
4. Acesse a aplicação:
  - Frontend: [http://localhost:8080](http://localhost:8080) 

  - Backend API: [http://localhost:8080/api/tarefas/](http://localhost:8080/api/tarefas/)
5. Para derrubar os containers, utilize o comando: 
```bash 
podman-compose down -v
```

