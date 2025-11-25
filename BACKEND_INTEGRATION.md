# 🔧 GUIA DE INTEGRAÇÃO - ROTAS DO BACKEND

## Adicione as rotas abaixo ao seu `script.py`

```python
# ============================================================================
# PAINEL ADMINISTRATIVO - ROTAS NECESSÁRIAS
# ============================================================================

# Rota principal do painel (index do admin)
@app.route("/funcao")
def func():
    """Página principal do painel administrativo com 4 opções"""
    return render_template("funcao.html")


# ============================================================================
# ROTA 1: GERENCIAMENTO DE PREÇOS
# ============================================================================

@app.route("/preco", methods=["GET", "POST"])
def preco():
    """Página de gerenciamento de preços por dia da semana"""
    
    if request.method == "POST":
        # Aqui você pode processar os preços submetidos
        # Exemplo: atualizar no banco de dados
        
        segunda = request.form.get("segunda")
        terca = request.form.get("terca")
        quarta = request.form.get("quarta")
        quinta = request.form.get("quinta")
        sexta = request.form.get("sexta")
        sabado = request.form.get("sabado")
        domingo = request.form.get("domingo")
        
        # Conectar ao banco e atualizar tabela_preco
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            dias = {
                "Segunda-feira": segunda,
                "Terça-feira": terca,
                "Quarta-feira": quarta,
                "Quinta-feira": quinta,
                "Sexta-feira": sexta,
                "Sábado": sabado,
                "Domingo": domingo
            }
            
            for dia, preco_valor in dias.items():
                cursor.execute("UPDATE tabela_preco SET preco = ? WHERE dia_semana = ?",
                             (float(preco_valor), dia))
            
            conn.commit()
            conn.close()
            flash("Preços atualizados com sucesso!", "success")
            
        except Exception as e:
            flash(f"Erro ao atualizar preços: {str(e)}", "error")
        
        return redirect(url_for("preco"))
    
    # GET - Carregar preços atuais
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT dia_semana, preco FROM tabela_preco ORDER BY ROWID")
        precos_db = dict(cursor.fetchall())
        conn.close()
    except:
        precos_db = {}
    
    return render_template("preco.html", precos=precos_db)


# ============================================================================
# ROTA 2: GERENCIAMENTO DE CLIENTES
# ============================================================================

@app.route("/gerenciar", methods=["GET", "POST"])
def gerenciar():
    """Página de gerenciamento de clientes com busca e filtros"""
    
    if request.method == "POST":
        # Lógica para editar cliente
        action = request.form.get("action")
        
        if action == "editar":
            cpf = request.form.get("cpf")
            nome = request.form.get("nome")
            email = request.form.get("email")
            telefone = request.form.get("telefone")
            status = request.form.get("status")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE usuarios 
                    SET nome = ?, email = ?, telefone = ?, status = ?
                    WHERE cpf = ?
                """, (nome, email, telefone, status, cpf))
                conn.commit()
                conn.close()
                flash("Cliente atualizado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao atualizar cliente: {str(e)}", "error")
        
        elif action == "bloquear":
            cpf = request.form.get("cpf")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE usuarios SET status = 'bloqueado' WHERE cpf = ?", (cpf,))
                conn.commit()
                conn.close()
                flash("Cliente bloqueado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao bloquear cliente: {str(e)}", "error")
        
        elif action == "remover":
            cpf = request.form.get("cpf")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM usuarios WHERE cpf = ?", (cpf,))
                conn.commit()
                conn.close()
                flash("Cliente removido com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao remover cliente: {str(e)}", "error")
        
        return redirect(url_for("gerenciar"))
    
    # GET - Buscar clientes
    busca_cpf = request.args.get("busca_cpf", "")
    busca_nome = request.args.get("busca_nome", "")
    filtro_status = request.args.get("filtro_status", "")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        query = "SELECT cpf, nome, email, telefone, status FROM usuarios WHERE 1=1"
        params = []
        
        if busca_cpf:
            query += " AND cpf LIKE ?"
            params.append(f"%{busca_cpf}%")
        
        if busca_nome:
            query += " AND nome LIKE ?"
            params.append(f"%{busca_nome}%")
        
        if filtro_status:
            query += " AND status = ?"
            params.append(filtro_status)
        
        cursor.execute(query, params)
        clientes = cursor.fetchall()
        
        # Contar reservas por cliente
        cliente_data = []
        for cliente in clientes:
            cpf = cliente[0]
            cursor.execute("SELECT COUNT(*) FROM reservas WHERE cliente_cpf = ?", (cpf,))
            num_reservas = cursor.fetchone()[0]
            cliente_data.append({
                "cpf": cliente[0],
                "nome": cliente[1],
                "email": cliente[2],
                "telefone": cliente[3],
                "status": cliente[4],
                "reservas": num_reservas
            })
        
        conn.close()
    except Exception as e:
        cliente_data = []
        flash(f"Erro ao carregar clientes: {str(e)}", "error")
    
    return render_template("gerenciar.html", clientes=cliente_data)


# ============================================================================
# ROTA 3: RELATÓRIOS E ESTATÍSTICAS
# ============================================================================

@app.route("/relatorios")
def relatorios():
    """Página de relatórios com estatísticas de vendas"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Receita total
        cursor.execute("""
            SELECT SUM(CAST(preco AS FLOAT))
            FROM reservas
            JOIN tabela_preco ON tabela_preco.dia_semana = 
                CASE WHEN strftime('%w', reservas.data) = '0' THEN 'Domingo'
                     WHEN strftime('%w', reservas.data) = '1' THEN 'Segunda-feira'
                     WHEN strftime('%w', reservas.data) = '2' THEN 'Terça-feira'
                     WHEN strftime('%w', reservas.data) = '3' THEN 'Quarta-feira'
                     WHEN strftime('%w', reservas.data) = '4' THEN 'Quinta-feira'
                     WHEN strftime('%w', reservas.data) = '5' THEN 'Sexta-feira'
                     WHEN strftime('%w', reservas.data) = '6' THEN 'Sábado'
                END
        """)
        receita_total = cursor.fetchone()[0] or 0
        
        # Total de ingressos
        cursor.execute("SELECT COUNT(*) FROM reservas")
        ingressos_total = cursor.fetchone()[0]
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE role = 'user'")
        clientes_total = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            "receita": receita_total,
            "ingressos": ingressos_total,
            "clientes": clientes_total,
            "ocupacao": 0  # Calcular com base no total de assentos
        }
    except Exception as e:
        stats = {
            "receita": 0,
            "ingressos": 0,
            "clientes": 0,
            "ocupacao": 0
        }
        flash(f"Erro ao carregar relatórios: {str(e)}", "error")
    
    return render_template("relatorios.html", stats=stats)


# ============================================================================
# ROTA 4: GERENCIAMENTO DE FILMES
# ============================================================================

@app.route("/filmes", methods=["GET", "POST"])
def gerenciar_filmes():
    """Página para gerenciar catálogo de filmes"""
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "novo":
            titulo = request.form.get("titulo")
            ano = request.form.get("ano")
            arquivo = request.form.get("arquivo")
            sinopse = request.form.get("sinopse")
            
            # Adicionar novo filme (se usar banco de dados)
            # Se usar lista em memória, reiniciar app para persistir
            
            flash("Filme adicionado com sucesso!", "success")
        
        elif action == "editar":
            filme_id = request.form.get("filme_id")
            # Lógica de edição
            flash("Filme atualizado com sucesso!", "success")
        
        elif action == "remover":
            filme_id = request.form.get("filme_id")
            # Lógica de remoção
            flash("Filme removido com sucesso!", "success")
        
        return redirect(url_for("gerenciar_filmes"))
    
    # GET - Mostrar todos os filmes
    return render_template("filmes.html", filmes=filmes)


# ============================================================================
# FIM DAS ROTAS DO PAINEL ADMINISTRATIVO
# ============================================================================
```

## 📝 Notas Importantes

1. **Banco de Dados**: 
   - Certifique-se de que a tabela `tabela_preco` existe com coluna `preco`
   - A tabela `usuarios` deve ter campos: `cpf`, `nome`, `email`, `telefone`, `status`
   - A tabela `reservas` deve ter campos: `cliente_cpf`, `data`, `filme_id`, `assento`

2. **Validações**:
   - Validar CPF antes de atualizar
   - Validar email antes de salvar
   - Validar preços (deve ser número positivo)

3. **Flash Messages**:
   - Adicione a exibição de mensagens flash no template base
   - Use `{% with messages = get_flashed_messages(with_categories=true) %}`

4. **Autenticação**:
   - Você deve adicionar verificação de permissão de admin
   - Use `@login_required` e verificar `current_user.role == 'admin'`

---

## 🔗 Exemplo de Estrutura de Flash Messages no Template

```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="alert alert-{{ category }}">
        {{ message }}
      </div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

---

**Dúvidas? Consulte a documentação oficial do Flask: https://flask.palletsprojects.com/**
