# MSI Auto-Installer - Deploy Guide

## 📋 PASSO A PASSO COMPLETO

### 🚀 PASSO 1: DEPLOY DO BACKEND

#### Opção A: Railway (Recomendado - Mais Fácil)
1. Acesse: https://railway.app
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Conecte seu GitHub e faça upload da pasta `/app/backend/`
6. Railway detectará automaticamente que é Python
7. Adicione as variáveis de ambiente:
   - `MONGO_URL`: mongodb://localhost:27017 (Railway fornece MongoDB grátis)
   - `DB_NAME`: msi_installer
8. Deploy automático será feito
9. Copie a URL gerada (ex: https://seu-app.railway.app)

#### Opção B: Heroku
1. Acesse: https://heroku.com
2. Crie conta gratuita
3. Instale Heroku CLI
4. No terminal:
   ```bash
   cd /caminho/para/backend
   heroku create seu-app-name
   heroku addons:create mongolab:sandbox
   git add .
   git commit -m "Deploy MSI Installer"
   git push heroku main
   ```
5. URL: https://seu-app-name.herokuapp.com

#### Opção C: Render
1. Acesse: https://render.com
2. Conecte GitHub
3. Selecione "Web Service"
4. Escolha o repositório com a pasta backend
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host=0.0.0.0 --port=$PORT`
6. Adicione MongoDB Atlas (grátis)

### 🌐 PASSO 2: TESTAR O BACKEND
Após deploy, teste se está funcionando:
- Acesse: https://sua-url.com/api/
- Deve retornar: `{"message": "MSI Download Service Online"}`

### 📱 PASSO 3: USAR O HTML
1. **Baixe o arquivo**: `msi-installer-complete.html`
2. **Opções de uso**:

#### Opção A: Teste Local
- Abra o arquivo direto no navegador
- Configure a URL do seu backend
- Teste todas as funcionalidades

#### Opção B: Hospedagem Simples
- **Netlify**: Arraste o HTML para netlify.app
- **Vercel**: Upload via vercel.com
- **GitHub Pages**: Commit no GitHub, ativar Pages

#### Opção C: Seu Servidor
- Upload para qualquer servidor web
- Funciona em Apache, Nginx, etc.

### ⚙️ PASSO 4: CONFIGURAÇÃO
1. Abra o HTML no navegador
2. Na seção "Configuração da API":
   - Cole a URL do seu backend (ex: https://seu-app.railway.app)
   - Mantenha "sample.msi" ou coloque seu arquivo
   - Clique em "Salvar Configuração"
3. Teste a conexão clicando em "Testar Conexão"

### 🔧 PASSO 5: PERSONALIZAÇÃO
Para usar seu próprio MSI:
1. Substitua o arquivo `sample.msi` no backend
2. Atualize o nome no HTML
3. Faça novo deploy

### 🎯 RESULTADO FINAL
- Backend rodando na nuvem ✅
- HTML funcionando em qualquer lugar ✅
- Download automático de MSI ✅
- Instalação automática no Windows ✅

### 📞 SUPORTE
Se tiver problemas:
1. Verifique se backend está online
2. Teste URLs no navegador
3. Confira console do navegador (F12)
4. Verifique se CORS está habilitado