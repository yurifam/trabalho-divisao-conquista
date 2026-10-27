# Publicar o trabalho no GitHub — conta `yurifam`

O projeto já tem um histórico Git local com commits genuínos feitos durante sua preparação. Ainda não foi criado um repositório remoto.

1. Acesse https://github.com/new e confirme que está conectado como **yurifam**.
2. Defina o nome do repositório: `trabalho-divisao-conquista` (ou outro nome de sua preferência). Escolha **Private** e compartilhe acesso com o professor, ou escolha **Public** se essa for a forma de entrega combinada.
3. **Não** adicione README, `.gitignore` nem licença pelo site: esses arquivos já estão dentro do ZIP, e começar sem um commit remoto evita conflitos.
4. Baixe e **extraia todo o ZIP**. Entre na pasta `divisao_conquista_entrega` (ela contém o diretório `.git`, possivelmente oculto).
5. No terminal, dentro dessa pasta, execute:

   ```bash
   git remote add origin https://github.com/yurifam/trabalho-divisao-conquista.git
   git branch -M main
   git push -u origin main
   ```

   Caso tenha criado o repositório com outro nome, altere a URL acima. O Git poderá solicitar a autenticação pelo navegador/Git Credential Manager. Não cole senhas ou tokens neste chat.

6. Confirme que a página do repositório mostra o PDF, os CSVs, o README, o código Python e os commits. Compartilhe a URL real com o professor. Para um repositório privado, também é preciso conceder acesso ao professor.

**Atenção:** os commits existentes registram a preparação efetiva atual; o trabalho pede histórico ao longo de semanas. O histórico anterior não pode ser inventado. Se os integrantes desenvolverem melhorias adicionais de fato, registrem essas mudanças normalmente.

**Identificação concluída:** a dupla está registrada no README e no relatório em PDF: Yuri Freitas Andrade Maia (2510459) e Fernando Jose Simon Heck (2510386).
