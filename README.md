# Monitora Manaus

O **Monitora Manaus** é um protótipo funcional de plugin desenvolvido como simulação de proposta e teste de produto aplicado à realidade urbana, elaborado como Trabalho Final da disciplina de **Planejamento e Gestão do Espaço Urbano** do Curso de Bacharelado em Geografia do Instituto de Ciências da Sociedade e Desenvolvimento Regional, Universidade Federal Fluminense (**UFF Campos dos Goytacazes/RJ**)[cite: 12].

O projeto tem como objetivo apoiar o **georreferenciamento de câmeras de segurança** no Centro de Manaus (AM), simulando uma ferramenta prática para gestão pública, estudos urbanos e auditorias urbanas que permite testar em ambiente SIG fluxos reais de consulta espacial e análise de adequação à Lei Geral de Proteção de Dados (LGPD)[cite: 12].

> **Nota sobre o escopo:** Trata-se de uma prova de conceito e simulação acadêmica para validação funcional da proposta, operando sobre uma base vetorial estruturada para reproduzir o comportamento do sistema em uso real.

## Principais funcionalidades

- **Base de dados vetorial integrada:** utiliza o arquivo GeoPackage (`cameras_manaus.gpkg`) em modo de consulta (somente leitura), sem alterar nem criar feições na base original.
- **Filtragem espacial combinada:** permite filtrar o georreferenciamento de câmeras de segurança por três eixos analíticos — **Esfera Gestora**, **Tipo de Equipamento** e **Sinalização da LGPD**.
- **Exibição sob demanda no mapa:** renderiza os pontos filtrados apenas após a interação do usuário na interface do plugin.

## Equipe e Licença

- **Grupo:** João Vitor Tuller Campista, Julia Yasmin Marques Siqueira, Julio Cesar Tuller Campista e Pedro Nazareno Mendes[cite: 12]
- **Licença:** GNU General Public License v3 (GPLv3)
- **Página oficial no QGIS:** https://plugins.qgis.org/plugins/monitora_manaus/
