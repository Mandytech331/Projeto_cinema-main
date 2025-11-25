import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from hashlib import sha256
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'
db_path = "cinedata.db"

def gerar_datas_com_preco(qtd=15):
    hoje = datetime.now().date()
    datas = []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    mapa = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    for i in range(qtd):
        data = hoje + timedelta(days=i)
        dia_semana_pt = mapa[data.strftime("%A")]

        cursor.execute("SELECT preco FROM tabela_preco WHERE dia_semana = ?", (dia_semana_pt,))
        resultado = cursor.fetchone()

        preco = resultado[0]

        datas.append({
            "data": data.isoformat(),
            "dia_semana": dia_semana_pt,
            "preco": preco
        })

    conn.close()
    return datas

def ocupados_sessao(filme_id, data, horario):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT assento FROM reservas
        WHERE filme_id = ? AND data = ? AND horario = ?
    """, (filme_id, data, horario))
    result = [r[0] for r in cursor.fetchall()]
    conn.close()
    return result

filmes = [
    {"id": 0, "arquivo": "clube.jpg", "titulo": "Clube da Luta", "ano": 1999, "sinopse": "Um homem deprimido que sofre de insônia conhece um estranho vendedor chamado Tyler Durden e se vê morando em uma casa suja depois que seu perfeito apartamento é destruído. A dupla forma um clube com regras rígidas onde homens lutam. A parceria perfeita é comprometida quando uma mulher, Marla, atrai a atenção de Tyler."},
    {"id": 1, "arquivo": "interestelar.jpg","titulo": "Interestelar", "ano": 2014, "sinopse": "As reservas naturais da Terra estão chegando ao fim e um grupo de astronautas recebe a missão de verificar possíveis planetas para receberem a população mundial, possibilitando a continuação da espécie. Cooper é chamado para liderar o grupo e aceita a missão sabendo que pode nunca mais ver os filhos. Ao lado de Brand, Jenkins e Doyle, ele seguirá em busca de um novo lar."},
    {"id": 2, "arquivo": "karate.jpg", "titulo": "Karatê Kid 5", "ano": 1994, "sinopse": "Um garoto de 12 anos chamado Dre Parker se muda para a China com a mãe e se vê em um terra estranha. Ele sabe um pouco de caratê, mas suas habilidades não são o bastante para enfrentar o valentão da escola, Cheng. Dre faz amizade com o Sr. Han, um mestre das artes marciais, que lhe ensina os segredos do kung fu na esperança de que o garoto possa derrotar Cheng e, quem sabe, conquistar o coração da linda Mei Ying."},
    {"id": 3, "arquivo": "addams.jpg", "titulo": "Família Addams", "ano": 1991, "sinopse": "Os Addams, uma família macabra, correm o risco de perder seu tesouro de moedas de ouro, pois Tully Alford (Dan Hedaya), um advogado desonesto de quem os Addams são clientes, está em sérias dificuldades financeiras. Como os credores de Alford, Abigail Craven e o filho Gordon estão dispostos a fazer qualquer coisa para receber o dinheiro, o advogado tem uma idéia ao notar que Gordon é muito parecido com Fester, o irmão perdido de Gomez Addams. Assim, Gordon finge ser Fester para tentar encontrar a fortuna de Gomez, Mortícia, Wandinha  e Pugsley Addams. Mas o plano não é tão simples como parece, pois os Addams são uma família bastante peculiar."},
    {"id": 4, "arquivo": "narnia.jpg", "titulo": "As Crônicas de Nárnia", "ano": 2005, "sinopse": "Durante os bombardeios da Segunda Guerra Mundial de Londres, quatro irmãos ingleses são enviados para uma casa de campo onde eles estarão seguros. Um dia, Lucy encontra um guarda-roupa que a transporta para um mundo mágico chamado Nárnia. Depois de voltar, ela logo volta a Nárnia com seus irmãos, Peter e Edmund, e sua irmã, Susan. Lá eles se juntam ao leão mágico, Aslan, na luta contra a Feiticeira Branca."},
    {"id": 5, "arquivo": "furiosos.jpg", "titulo": "Velozes e Furiosos 5", "ano": 2011, "sinopse": "Desde que o ex-policial Brian O'Conner e Mia Toretto libertaram Dom da prisão, eles viajam pelo mundo para fugir das autoridades. No Rio de Janeiro, são obrigados a fazer um último trabalho antes de ganhar sua liberdade definitiva. Brian e Dom montam uma equipe de elite de pilotos de carro para executar a tarefa, mas precisam enfrentar um empresário corrupto e também um obstinado agente federal norte-americano."},
    {"id": 6, "arquivo": "invocacao.jpg", "titulo": "Invocação do Mal 2", "ano": 2016, "sinopse": "Os famosos demonologistas Lorraine e Ed Warren viajam até o norte de Londres. Lá, eles ajudam uma mãe solteira que cria quatro filhos sozinha em uma casa atormentada por espíritos malignos."},
    {"id": 7, "arquivo": "schindler.jpg", "titulo": "A Lista de Schindler", "ano": 1993, "sinopse": "O alemão Oskar Schindler viu na mão de obra judia uma solução barata e viável para lucrar com negócios durante a guerra. Com sua forte influência dentro do partido nazista, foi fácil conseguir as autorizações e abrir uma fábrica. O que poderia parecer uma atitude de um homem não muito bondoso, transformou-se em um dos maiores casos de amor à vida da História, pois este alemão abdicou de toda sua fortuna para salvar a vida de mais de mil judeus em plena luta contra o extermínio alemão."},
    {"id": 8, "arquivo": "homem.jpg", "titulo": "Até o Último Homem", "ano": 2016, "sinopse": "Acompanhe a história de Desmond T. Doss, um médico do exército americano que, durante a Segunda Guerra Mundial, se recusa a pegar em armas. Durante a Batalha de Okinawa ele trabalha na ala médica e salva cerca de 75 homens."},
]

def validacao_cpf(cpf):
    numeros = [int(d) for d in cpf if d.isdigit()]
    if len(numeros) != 11:
        return False
    if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        return False

    soma1 = sum(a * b for a, b in zip(numeros[:9], range(10, 1, -1)))
    digito1 = (soma1 * 10 % 11) % 10
    if numeros[9] != digito1:
        return False

    soma2 = sum(a * b for a, b in zip(numeros[:10], range(11, 1, -1)))
    digito2 = (soma2 * 10 % 11) % 10
    return numeros[10] == digito2


@app.route("/")
def login():
    return render_template('login.html')

@app.route("/registro")
def regis():
     return render_template('registro.html')

@app.route("/index")
def principal():
     return render_template("principal.html", filmes=filmes)

@app.route("/funcao")
def func():
    return render_template("funcao.html")

@app.route("/comprar")
def comp():
    return render_template("comprar.html")

@app.route("/reserva")
def reservas():
    return render_template("reservas.html")

@app.route('/inserir', methods=['POST'])
def inserir():
        user = request.form.get('user')
        senha = request.form.get('pass')
        
        senha_hash = sha256(senha.encode('utf-8')).hexdigest()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cpf, idfunc FROM usuario WHERE login = ? AND senha = ?", (user, senha_hash))
        usuario = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if usuario:  
            session["cpf"] = usuario[0] 
            session["user_funcao"] = usuario[1]

            if  usuario[1] == 2:
                return redirect(url_for('principal'))
            else:
                return redirect(url_for('func'))
        else:
             flash('Usuário ou senha incorretos!')
             return redirect(url_for('login'))
        
@app.route('/registrar', methods=['POST'])
def registrar():
    cpf = request.form.get('cpf')            
    name = request.form.get('name')
    user = request.form.get('user')
    senha = request.form.get('pass')
    func = 1

    if not validacao_cpf(cpf):
        flash(f"O CPF {cpf} não é válido... Tente outro CPF...")
        return redirect(url_for('regis'))
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE login = ?", (user,))
        if cursor.fetchone()[0] > 0:
            flash("Nome de usuário já existe. Escolha outro.")
            return redirect(url_for('regis'))

        senha_hash = sha256(senha.encode('utf-8')).hexdigest()
        try:
            cursor.execute('''INSERT INTO usuario (cpf, nome, login, senha, idfunc) VALUES (?, ?, ?, ?, ?)''', (cpf, name, user, senha_hash, func))
            conn.commit()
            flash("Registro feito com sucesso!")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Erro ao registrar: CPF já registrado")
            return redirect(url_for('regis'))
        
@app.route("/filme/<int:filmes_id>")
def comprar(filmes_id):
    filme =filmes[filmes_id]
    datas = gerar_datas_com_preco()

    horarios = ["14:30", "18:00", "20:30", "22:30"]

    return render_template("comprar.html", filme=filme,datas=datas, horarios=horarios)

@app.route("/assentos", methods=["GET"])
def assentos():
    filme_id = int(request.args.get("filme_id"))
    data = request.args.get("data")
    dia_semana = request.args.get("dia_semana")
    preco = float(request.args.get("preco", 0.0))
    horario = request.args.get("horario")

    ocupados = ocupados_sessao(filme_id, data, horario)
    return render_template("assentos.html", filme=filmes[filme_id], data=data, horario=horario, dia_semana=dia_semana, preco=preco, ocupados=ocupados)

@app.route("/reservar", methods=["POST"])
def reservar():
    cpf = session.get("cpf") 
    filme_id = int(request.form.get("filme_id"))
    data = request.form.get("data")
    horario = request.form.get("horario")
    preco = float(request.form.get("preco", 0.0))
    assentos_str = request.form.get("assentos", "")

    if not assentos_str or assentos_str.strip() == "":
        flash("Você precisa selecionar pelo menos um assento!")
        return redirect(request.referrer)

    try:
        assentos = sorted({int(s) for s in assentos_str.split(",") if s.strip()})
    except ValueError:
        flash("Assentos inválidos.", "danger")
        return redirect(request.referrer or url_for("index"))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    qmarks = ",".join("?"*len(assentos))
    params = [filme_id, data, horario] + assentos
    # build query to find conflicts
    query = f"""
        SELECT assento FROM reservas
        WHERE filme_id = ? AND data = ? AND horario = ? AND assento IN ({qmarks})
    """
    cursor.execute(query, params)
    conflitos = [r[0] for r in cursor.fetchall()]

    if conflitos:
        conn.close()
        flash(f"Assentos já reservados: {', '.join(map(str, conflitos))}", "danger")
        return redirect(request.referrer or url_for("comp", filme_id=filme_id))

    try:
        param_list = [(cpf, filme_id, data, horario, a) for a in assentos]

        cursor.executemany("""
            INSERT INTO reservas (cpf, filme_id, data, horario, assento)
            VALUES (?, ?, ?, ?, ?)
        """, param_list)

        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        flash("Alguns assentos já foram reservados. Tente novamente.", "danger")
        conn.close()
        return redirect(request.referrer or url_for("comp", filme_id=filme_id))
    
    total = len(assentos) * preco
    conn.close()
    flash(f"Reservado: {', '.join(map(str, assentos))}. Total: R$ {total:.2f}", "success")
    return redirect(url_for("login"))

@app.route("/reservas")
def minhas_reservas():
    cpf = session.get("cpf")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.data, r.horario, r.assento, r.filme_id
        FROM reservas r
        WHERE r.cpf = ?
        ORDER BY r.data, r.horario
    """, (cpf,))

    reservas = cursor.fetchall()
    conn.close()

    return render_template("reservas.html", reservas=reservas)

if __name__ == "__main__":
    app.run(debug=True)