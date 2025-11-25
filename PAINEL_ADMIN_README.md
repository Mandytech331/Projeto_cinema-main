#  Novas Funcionalidades do Painel Administrativo

##  Funcionalidades Adicionadas

### 1. **Página de Função (Painel Principal)**
   - **Arquivo**: `templates/funcao.html`
   - **CSS**: `static/css/funcao.css`
   - **Descrição**: Página inicial do painel admin com 4 cards de acesso rápido
   - **Cards**:
     - 💰 Tabela de Preços
     - 👥 Gerenciar Clientes
     - 📊 Relatórios
     - 🎬 Gerenciar Filmes

### 2. **Página de Preços**
   - **Arquivo**: `templates/preco.html`
   - **CSS**: `static/css/preco.css`
   - **Descrição**: Interface para gerenciar preços por dia da semana
   - **Funcionalidades**:
     - Formulário com 7 campos (um para cada dia da semana)
     - Validação de entrada
     - Botão de salvar e restaurar

### 3. **Página de Relatórios**
   - **Arquivo**: `templates/relatorios.html`
   - **CSS**: `static/css/relatorios.css`
   - **Descrição**: Dashboard com estatísticas de vendas
   - **Funcionalidades**:
     - Filtros por data, filme
     - Cards de métricas (receita, ingressos, clientes, ocupação)
     - Tabela de desempenho por filme
     - Informações de período de pico

### 4. **Página de Gerenciar Filmes**
   - **Arquivo**: `templates/filmes.html`
   - **CSS**: `static/css/filmes.css`
   - **Descrição**: Interface para gerenciar catálogo de filmes
   - **Funcionalidades**:
     - Grid de filmes com poster
     - Botões para editar/remover
     - Modal para adicionar/editar filmes
     - Busca e ordenação

### 5. **Página de Gerenciar Clientes (Melhorada)**
   - **Arquivo**: `templates/gerenciar.html`
   - **CSS**: `static/css/gerenciar.css`
   - **Descrição**: Interface completa de gerenciamento de clientes
   - **Funcionalidades**:
     - Barra de busca por CPF e nome
     - Filtro por status
     - Tabela com ações (editar, bloquear, remover)
     - Modal para editar cliente
     - Paginação
     - Estatísticas
     - Botões de exportar/importar dados

---

##  Design & Estilo

### Paleta de Cores Consistente
- **Primário**: Roxo `#a259ff`
- **Secundário**: Roxo escuro `#8b3ff6`
- **Fundo**: Preto `#0a0a0f`
- **Texto**: Branco `#ffffff`
- **Muted**: Cinza `#cccccc`

### Características Visuais
- ✅ Gradientes lineares nos cards e botões
- ✅ Animações suaves (fadeInDown, slideUp)
- ✅ Efeito glass-morphism com backdrop-filter
- ✅ Sombras dinâmicas e elevação ao hover
- ✅ Responsividade total (mobile-first)
- ✅ Acessibilidade (prefers-reduced-motion)

### Breakpoints Responsivos
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px

---

##  Rotas Backend Necessárias

Para que o projeto funcione completamente, adicione ao `script.py`:

```python
@app.route("/preco", methods=["GET", "POST"])
def preco():
    if request.method == "POST":
        # Processa atualização de preços
        pass
    return render_template("preco.html")

@app.route("/relatorios")
def relatorios():
    return render_template("relatorios.html")

@app.route("/filmes", methods=["GET", "POST"])
def gerenciar_filmes():
    if request.method == "POST":
        # Processa novo/editar filme
        pass
    return render_template("filmes.html", filmes=filmes)

@app.route("/gerenciar", methods=["GET", "POST"])
def gerenciar():
    if request.method == "POST":
        # Processa pesquisa/edição de cliente
        pass
    return render_template("gerenciar.html")
```

---

##  Instruções de Uso

1. **Acessar o Painel**: Navegue para `/funcao`
2. **Cada Card**: Clique para acessar a funcionalidade desejada
3. **Voltar**: Clique no botão "← Voltar" em cada página
4. **Sair**: Clique em "Sair" no canto superior direito

---

##  Responsividade Testada

- ✅ Desktop (1920px, 1366px)
- ✅ Tablet (768px, 1024px)
- ✅ Mobile (480px, 360px)

---

##  Próximos Passos

1. Integrar rotas no backend (`script.py`)
2. Conectar banco de dados para salvar dados
3. Implementar funcionalidades de filtro e busca
4. Adicionar autenticação de admin
5. Implementar paginação na tabela de clientes

---


