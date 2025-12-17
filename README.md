# E-Commerce API - MVP

API REST completa desenvolvida em Flask para gerenciamento de pedidos de um sistema de e-commerce. Projeto desenvolvido como parte do trabalho de conclusão da pós-graduação.

## 📋 Descrição

Sistema web componentizado que oferece uma API REST para gerenciamento de pedidos, validação de endereços via ViaCEP e integração com catálogo de produtos do FakeStore. A API foi projetada para se comunicar com um front-end React e seguir as melhores práticas de desenvolvimento.

## 🚀 Tecnologias Utilizadas

- **Python 3.11+** - Linguagem de programação
- **Flask 3.0.0** - Framework web
- **Flask-SQLAlchemy** - ORM para banco de dados
- **MySQL** - Banco de dados relacional
- **PyMySQL** - Driver MySQL para Python
- **Flask-CORS** - Gerenciamento de CORS
- **Marshmallow** - Validação e serialização de dados
- **Requests** - Cliente HTTP para APIs externas
- **Docker** - Containerização
- **ViaCEP API** - Validação de CEP
- **FakeStore API** - Catálogo de produtos

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Python 3.11 ou superior
- MySQL 8.0 ou superior
- Docker e Docker Compose (opcional)
- Git

## 🔧 Instalação e Configuração

### Método 1: Instalação Local (sem Docker)

#### 1. Clonar o Repositório

```bash
git clone https://github.com/Igorseven/Ecommerce-API.git
cd Ecommerce-API
```

#### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar Banco de Dados MySQL

```sql
-- Conectar ao MySQL
mysql -u root -p

-- Criar banco de dados
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário
CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'senha123456';
GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'ecommerce_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 5. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
```

Exemplo de `.env`:

```env
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=minha-chave-secreta-super-segura

DATABASE_URL=mysql+pymysql://root:root123@localhost:3306/ecommerce_db

CORS_ORIGINS=http://localhost:3000,http://localhost:3001

VIACEP_API_URL=https://viacep.com.br/ws
```

#### 6. Executar a Aplicação

```bash
python run.py
```

A API estará disponível em: `http://localhost:5000`

### Método 2: Usando Docker

#### 1. Build da Imagem

```bash
docker build -t ecommerce-api .
```

#### 2. Executar Container

```bash
docker run -d \
  --name ecommerce-api \
  -p 5000:5000 \
  -e DATABASE_URL=mysql+pymysql://root:password@host.docker.internal:3306/ecommerce_db \
  -e FLASK_ENV=production \
  ecommerce-api
```

#### 3. Verificar Logs

```bash
docker logs -f ecommerce-api
```

#### 4. Parar Container

```bash
docker stop ecommerce-api
docker rm ecommerce-api
```

## 📖 Documentação das Rotas (Endpoints)

### Rotas Principais

#### 1. Raiz da API

```http
GET /
```

Retorna informações sobre a API e endpoints disponíveis.

**Resposta (200 OK):**
```json
{
  "message": "E-Commerce API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "orders": "/api/orders",
    "cep": "/api/cep",
    "products": "/api/products",
    "health": "/health"
  }
}
```

#### 2. Health Check

```http
GET /health
```

Verifica o status da API e conexão com banco de dados.

**Resposta (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### Rotas de Pedidos (`/api/orders`)

#### 1. Criar Pedido

```http
POST /api/orders
Content-Type: application/json
```

**Body:**
```json
{
  "customer_name": "João Silva",
  "customer_email": "joao@email.com",
  "customer_phone": "11999999999",
  "address": {
    "cep": "01310100",
    "number": "123",
    "complement": "Apto 45"
  },
  "items": [
    {
      "product_id": 1,
      "product_name": "Notebook Dell",
      "product_image": "https://example.com/image.jpg",
      "quantity": 2,
      "unit_price": 2500.00
    }
  ]
}
```

**Resposta (201 Created):**
```json
{
  "message": "Pedido criado com sucesso",
  "order": {
    "id": 1,
    "order_number": "ORD-20231215-A1B2",
    "customer_name": "João Silva",
    "customer_email": "joao@email.com",
    "customer_phone": "11999999999",
    "total_amount": 5010.00,
    "shipping_cost": 10.00,
    "status": "pending",
    "created_at": "2023-12-15T10:30:00",
    "updated_at": "2023-12-15T10:30:00",
    "address": {
      "id": 1,
      "cep": "01310-100",
      "street": "Avenida Paulista",
      "number": "123",
      "complement": "Apto 45",
      "neighborhood": "Bela Vista",
      "city": "São Paulo",
      "state": "SP"
    },
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Notebook Dell",
        "product_image": "https://example.com/image.jpg",
        "quantity": 2,
        "unit_price": 2500.00,
        "total_price": 5000.00
      }
    ]
  }
}
```

#### 2. Listar Pedidos

```http
GET /api/orders?status=pending&limit=10&offset=0&order_by=created_at&sort=desc
```

**Query Parameters:**
- `status` (opcional): Filtrar por status (pending, confirmed, processing, shipped, delivered, cancelled)
- `limit` (opcional): Número máximo de resultados (padrão: 10, máximo: 100)
- `offset` (opcional): Número de registros a pular (padrão: 0)
- `order_by` (opcional): Campo para ordenação (created_at, total_amount)
- `sort` (opcional): Direção da ordenação (asc, desc)

**Resposta (200 OK):**
```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "ORD-20231215-A1B2",
      "customer_name": "João Silva",
      "customer_email": "joao@email.com",
      "total_amount": 5010.00,
      "shipping_cost": 10.00,
      "status": "pending",
      "created_at": "2023-12-15T10:30:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### 3. Buscar Pedido por ID

```http
GET /api/orders/1
```

**Resposta (200 OK):**
```json
{
    "order": {
        "address": {
            "cep": "06036-010",
            "city": "São paulo",
            "complement": "",
            "id": 1,
            "neighborhood": "Centro",
            "number": "659",
            "state": "SP",
            "street": "Avenida Dos Testes"
        },
        "created_at": "2025-12-17T14:35:13",
        "customer_email": "igor@gmail.com",
        "customer_name": "Igor Seven",
        "customer_phone": "1191777777",
        "id": 1,
        "items": [
            {
                "id": 1,
                "product_id": 1,
                "product_image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_t.png",
                "product_name": "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
                "quantity": 1,
                "total_price": 109.95,
                "unit_price": 109.95
            },
            {
                "id": 2,
                "product_id": 2,
                "product_image": "https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_t.png",
                "product_name": "Mens Casual Premium Slim Fit T-Shirts ",
                "quantity": 1,
                "total_price": 22.3,
                "unit_price": 22.3
            }
        ],
        "order_number": "ORD-20251217-RJRZ",
        "shipping_cost": 10.0,
        "status": "pending",
        "total_amount": 142.25,
        "updated_at": "2025-12-17T14:35:13"
    }
}
```

#### 4. Atualizar Pedido

```http
PUT /api/orders/1
Content-Type: application/json
```

**Body:**
```json
{
  "customer_name": "João Silva Jr.",
  "customer_email": "joao.jr@email.com",
  "customer_phone": "11888888888",
  "status": "confirmed"
}
```

**Resposta (200 OK):**
```json
{
  "message": "Pedido atualizado com sucesso",
  "order": { ... }
}
```

#### 5. Deletar Pedido

```http
DELETE /api/orders/1
```

**Resposta (204 No Content)**

---

### Rotas de CEP (`/api/cep`)

#### 1. Validar e Buscar CEP

```http
GET /api/cep/01310100?calculate_shipping=true
```

**Query Parameters:**
- `calculate_shipping` (opcional): Se true, inclui cálculo de frete (padrão: false)

**Resposta (200 OK):**
```json
{
  "valid": true,
  "cep": "01310-100",
  "street": "Avenida Paulista",
  "complement": "",
  "neighborhood": "Bela Vista",
  "city": "São Paulo",
  "state": "SP",
  "ibge": "3550308",
  "gia": "1004",
  "ddd": "11",
  "shipping": {
    "state": "SP",
    "original_cost": 10.00,
    "final_cost": 10.00,
    "free_shipping": false,
    "message": "Valor do frete para SP"
  },
  "estimated_delivery_days": 2
}
```

#### 2. Calcular Frete por Estado

```http
GET /api/cep/shipping/SP?total_amount=250.00
```

**Resposta (200 OK):**
```json
{
  "state": "SP",
  "original_cost": 10.00,
  "final_cost": 0.00,
  "free_shipping": true,
  "message": "Frete grátis para compras acima de R$ 200.00",
  "estimated_delivery_days": 2
}
```

#### 3. Listar Tabela de Fretes

```http
GET /api/cep/shipping/rates
```

**Resposta (200 OK):**
```json
{
  "SP": 10.00,
  "RJ": 15.00,
  "MG": 15.00,
  "ES": 20.00,
  "default": 25.00
}
```

---

## 🌐 APIs Externas Utilizadas

### 1. ViaCEP

**Descrição:** API pública brasileira para consulta de CEP.

**Documentação:** https://viacep.com.br

**Uso no projeto:**
- Validação automática de CEP
- Preenchimento de endereço
- Base para cálculo de frete

---

## 🎯 Funcionalidades Implementadas

### Requisitos Obrigatórios
- ✅ Framework Flask
- ✅ Banco de dados MySQL com SQLAlchemy
- ✅ Mínimo 4 métodos HTTP diferentes (POST, GET, PUT, DELETE)
- ✅ Integração com ViaCEP (obrigatória)
- ✅ CRUD completo de pedidos
- ✅ Dockerfile funcional

### Diferenciais Implementados
- ✅ Validação de dados com Marshmallow
- ✅ Paginação nas listagens
- ✅ Filtros avançados (por status, data)
- ✅ Ordenação customizável
- ✅ Logs estruturados
- ✅ Cálculo de frete com faixas de CEP
- ✅ Frete grátis para compras acima de R$ 200
- ✅ Geração de número de pedido único
- ✅ Timestamps automáticos (created_at, updated_at)
- ✅ Soft relationships com cascade delete
- ✅ Health check endpoint
- ✅ Error handlers personalizados

---

## 🔒 Segurança

### Boas Práticas Implementadas

- Uso de variáveis de ambiente para credenciais
- Validação de entrada com Marshmallow
- CORS configurado adequadamente
- Logging de erros e acessos
- Healthcheck para monitoramento
- Tratamento de exceções

### Recomendações para Produção

- Usar HTTPS
- Implementar autenticação JWT
- Rate limiting
- Validação de CSRF
- Sanitização de inputs
- Backup regular do banco
- Monitoramento e alertas

---

## 🐛 Troubleshooting

### Erro: "Access denied for user"

**Solução:** Verifique as credenciais do MySQL no arquivo `.env`

### Erro: "Can't connect to MySQL server"

**Solução:** Certifique-se de que o MySQL está rodando:
```bash
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql
```

### Erro: "ModuleNotFoundError"

**Solução:** Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "Port 5000 already in use"

**Solução:** Altere a porta no `.env` ou mate o processo:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

---

## 📚 Estrutura do Banco de Dados

### Diagrama ER

```
┌─────────────────┐
│     orders      │
├─────────────────┤
│ id (PK)         │
│ order_number    │
│ customer_name   │
│ customer_email  │
│ customer_phone  │
│ total_amount    │
│ shipping_cost   │
│ status          │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│   addresses     │       │   order_items   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ order_id (FK)   │       │ order_id (FK)   │
│ cep             │       │ product_id      │
│ street          │       │ product_name    │
│ number          │       │ product_image   │
│ complement      │       │ quantity        │
│ neighborhood    │       │ unit_price      │
│ city            │       │ total_price     │
│ state           │       └─────────────────┘
└─────────────────┘
```

---

## 👨‍💻 Autor

**Igor Henrique de Souza Silva**
- Email: igorsevenn@gmail.com
- LinkedIn: [linkedin.com/in/igor-sevenn](https://www.linkedin.com/in/igor-sevenn)
- GitHub: [github.com/Igorseven](https://github.com/Igorseven)

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do trabalho de conclusão da pós-graduação.

---