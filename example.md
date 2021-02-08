
# Introduction à Neo4J par la visualisation d'un schéma de Base de données. 

Un schéma vaut mille discours. Mais un schéma prend du temps à dessiner. Ce temps là est souvent sacrifié sur l'autel de la productivité par de nombreuses équipes de développement.
Certains outils permettent de générer automatiquement de la documentation. Seulement, certains contexte et environnement de développement ne permettent pas l'utilisation de ces outils (normes de sécurité, outils pauvres en fonctionnalités, prix, etc.).
Nous allons voir dans cet article les étapes qui nous permettront de générer une documentation automatiquement avec des outils qui nécessitent peu (voire aucun) de temps d'installation ou de configuration. 

# Sommaire
*Paste your index result here*
# I - Présentation

## A - Pile logicielle
Il y a dans notre stack logicielle deux entités principales. La base de données source (là où sont les données et métadonnées que l'on veut analyser), et la base de données de visualisation (là où on veut analyser notre base de données source). 
* **(Source) SGBD SQL Server** : J'utilise une base de données Microsoft SQL Server. Cela pourra être impactant dans la syntaxe des requêtes. Le schéma sys contient toutes les informations nécessaires sur la structure de la base de données dans laquelle il est situé. Ce schéma est très utile mais peut varier d'un SGBD à un autre. Un autre schéma très utile est le `INFORMATION_SCHEMA` qui est assez similaire mais est peut être moins optimisé du fait des clefs qui sont des varchar. 
* **(Source) BDD de type Datawarehouse** : pour ce qui est de la structure de la base de données, j'utilise un datawarehouse (entrepôt de données). Ce type de bases sont réputés pour sa grosse volumétrie, tant en terme de données qu'en terme de métadonnées (tables, colonnes, clef étrangères etc.). 
* **résultats de la requête en CSV** : Un des gros avantages de l'utilisation de SQL Server Management Studio (SSMS, le client SQL Server de Microsoft) est qu'il permet une conversion instantanée des résultats sous plusieurs formes. Nous allons utiliser un fichier CSV dans un premier temps pour récupérer ces résultats. Dans un second temps, et si l'on veut passer en full-automation, il serait intéressant d'utiliser les drivers SQL Server pour python afin de récupérer les données directement dans la requête. la principale raison de ce choix se porte sur sur le fait que la base de données est souvent inaccessible par les scripts des analystes (pour des questions de sécurité).
*  **Script de génération du texte en Python** : Nous allons utiliser le langage python pour faire notre script de génération des requêtes pour Neo4j. C'est un langage qui permet des développements rapides et souples. de plus, il est facilement utilisable en ligne (via des interpréteurs python, Google Colab., etc.) et donc ne nécessite pas forcément d'installation. 
* **Neo4J** : Pour ce tuto, je conseil deux utilisations possibles de Neo4J. La première est l'utilisation d'un container Docker (<a href="https://hub.docker.com/_/neo4j">DockerHub/Neo4J</a>). La deuxième est l'utilisation de leur projet gratuit "Sandbox" directement sur leur site (<a href="https://neo4j.com/sandbox/">Neo4J/SandBox</a>). Chacune des solutions est gratuite. Je préfère néanmoins l'utilisation de Docker si possible, car le SandBox neo4J reste un outil en ligne soumis à votre bande passante et à la capacité du serveur qui vous est alloué (mais je chipote).

## B - Connaissez vous Neo4J ?
 Neo4J est un SGBD "Not only SQL" (NoSQL) orientée graphs se reposant sur le langage Cypher pour le requêtage. Au lieu de requêter sur des tables (comme dans le SQL classique), on requêtes des noeuds qui sont reliés par des relations. Chaque noeud étant un enregistrement, mais peut appartenir à un type de noeud. Cet outil a principalement trois points forts. 
* **Son frontend** qui donne un feedback instantané et de quoi bien analyser les données présentés sous forme de graphs, de texte (JSON) ou de table "classiques". Le client du SGBD se matérialise sous la forme d'une application web qui permet de requêter, gérer, et visualiser le contenu de nos bases. 
* **Son backend**, lui, utilise une architecture graph, et est par conséquent extrêmement performant en terme de requêtage (select), même avec un gros montant de données (même si, pour notre tuto, nous n'avons pas tant que ça). En contrepartie, c'est pour l'insertion qu'une BDD graph sera naturellement moins efficace. Cela n'est pas gênant dans notre cas d'utilisation, du fait qu'un schéma de BDD n'est pas sensé changer très fréquemment.
* **L'ontologie** ou la structuration des données. Cette structuration est extrêmement facilitante et est sous la forme d'un ensemble de couple clef valeurs (JSON). On peut ainsi décrire les nœuds et les relations avec facilité. Ces ontologies peuvent être "rigidifiées" par l'utilisation de JSON Schema, même si cela va à l'encontre d'une des force de l'outil qui est sa souplesse. 

Pour ce qui est du langage Cypher (requêtage), il est très différent du langage SQL classique, mais reste intuitif et facile à prendre en main, du moment qu'on y accorde un peu de temps. 

Dans le cadre de notre implémentation, nous n'allons exploiter qu'une partie infime de sa puissance. Il serait possible même de ne pas passer par cette outil, et juste dessiner des graphs via d3.js. Cependant il est intéressant de prendre en main un outil comme celui ci. En outre, n'étant pas expert du Javascript, je préfère déléguer ce travail aux librairies frontend de Neo4J. 

# II - Implémentation
## A - Récupération du schéma de BDD par les tables sys
Nous allons utiliser la table `sys.tables`, `sys.columns`, `sys.foreign_key_columns`,  `sys.foreign_keys` pour faire cette requête. Si vous n'êtes pas familier avec le schéma sys, n'hésitez pas à aller voir la documentation SQL Server. 
```sql
SELECT 
	schema_name(tab.schema_id) + '.' + tab.name AS [table]
	, col.column_id
	, col.name AS column_name
	, CASE
		WHEN fk.object_id IS NOT NULL THEN '>-' 
		ELSE null 
	END AS rel
	, schema_name(pk_tab.schema_id) + '.' + pk_tab.name AS primary_table
	, pk_col.name AS pk_column_name
	, fk_cols.constraint_column_id AS no
	, fk.name AS fk_constraint_name
FROM sys.tables tab
INNER JOIN sys.columns col ON col.object_id = tab.object_id
LEFT OUTER JOIN sys.foreign_key_columns fk_cols
	ON fk_cols.parent_object_id = tab.object_id
	AND fk_cols.parent_column_id = col.column_id
LEFT OUTER JOIN sys.foreign_keys fk ON fk.object_id = fk_cols.constraint_object_id
LEFT OUTER JOIN sys.tables pk_tab ON pk_tab.object_id = fk_cols.referenced_object_id
LEFT OUTER JOIN sys.columns pk_col
	ON pk_col.column_id = fk_cols.referenced_column_id
	AND pk_col.object_id = fk_cols.referenced_object_id
WHERE schema_name(tab.schema_id) = 'dw' -- !!! A REMPLACER PAR VOTRE NOM DE SCHEMA !!!
ORDER BY schema_name(tab.schema_id) + '.' + tab.name,
col.column_id
```
La requête sélectionne le nom des tables, des colonnes du schéma, récupère l'identifiant de la clef étrangère, et grâce a cet identifiant, récupère les noms des objets via une deuxième jointure. 
 
## B - Conception des requêtes Cypher unitaires
* Ontologie de notre nœud DWTable sur Neo4J
```json
DWTable : { 
	name: 'NomDelaTable',
	columns : ['colonne1', 'colonne2']
}
```
* Ontologie de la liaison REFERENCES 
```json
REFERENCES : {  
	target : 'NomTableCible',
	on : 'NomColonneEtrangère'
}
```
Une table peut avoir plusieurs références sur d'autres tables 

### 1. Création de nœud et de relation en Cypher
Nous aborderons la philosophie et les principes de la syntaxe Cypher un peu plus tard. N'ayez pas peur de ne pas comprendre ces requêtes pour l'instant. 

* **Création d'un noeud**

D'après la documentation Neo4J/Cypher, la requête ci-dessous crée un noeud :
```php
CREATE (<Variable>:<Object> {attributes});
``` 
On crée un noeud du type "objet", ayant pour attributs ceux qu'on lui précise (format clef-valeur type JSON). Le résultat de cette requête peut être variabilisé dans Variable. 
Dans notre cas, on devrait avoir une requête de ce genre :
```php
CREATE (:DWTable {name:"", columns:['colonne1', 'colonne2']});
``` 

* **Création d'un lien**

Créer un lien avec Cypher est un peu plus complexe. Basiquement, on pourrait exécuter la requête 
```php 
# Syntaxe générique : 
CREATE (<var>:<Object> {<attr>}) -[<var>:<Object{<attr>}]->  (<var>:<Object> {<attr>})

# Dans notre cas : 
CREATE (noeud1:)-[r:references]->(noeud2:) ;
``` 

Cependant dans ce cas, l'interpréteur va créer tout ce qui a est variabilisé dans la requête. Ce n'est pas ce que nous voulons. Les nœuds seront déjà crées et nous ne les voulons pas en double. On va donc devoir trouver ces instances (nœud1 et nœud2) afin de pouvoir les reliées entre elles. Pour cela nous utiliserons un match en variabilisant les deux noeuds. Ces variables seront enfin utilisé dans la sous-requête de création du lien. 
```php
MATCH
	(n1: DWTable {name:'nomTable1'}), 
	(n2: DWTable {name:'NomTable2'}) 
CREATE (n1)-[r:references {on : 'ClefEtrangère'}]->(n2);
```
> NB : n'oubliez pas le ";" pour terminer une requête lorsque vous scriptez et regroupez plusieurs requêtes ! 

## C - Édition automatique des requêtes en python
Maintenant que nous avons nos requêtes génériques, nous pouvons scripter leur création. Pour se faire, nous utilisons un script Python qui vise à itérer sur un fichier CSV, créer en premier lieu les nœuds, puis, une fois que tous les nœuds sont en place, nous créons les liaisons. 
```py
import csv

with open('data', mode='r') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	table_columns = dict()

	# Itération sur chaque lignes, deserialisation du CSV en objet clef-valeur 
	for row in csv_reader : 
		# création de l'objet DWTable (indexé par son nom) s'il n'existe pas encore
		if row['table'] not in table_columns.keys() : 
			table_columns[row['table']] = {'columns':[], 'links': []}

		# Affectation de la colonne traitée à l'objet DWTable
		table_columns[row['table']]['columns'].append(row['column_name'])

		# Affectation de la clef étrangère à l'objet DWTable
		if row['fk_constraint_name'] != 'Null' : 
			table_columns[row['table']]['links'].append({'target' : row['primary_table'].split('.')[1], 'on' : row['pk_column_name']})
  
	# Itération sur les éléments de l'objet clef-valeur, 
	# Formattage des requêtes pour chaque tables 
	str_result = ""

	# Création des noeuds 
	for table_key in table_columns.keys() : 
		str_result += "CREATE (:DWTable {name : '" + table_key.split('.')[1] + "', columns : " + str(table_columns[table_key]['columns']) + "});\n" 

	# Création des liaisons entre les noeuds
	for table_key in table_columns.keys():
		if len(table_columns[table_key]['links']) > 0 : 
			for link in table_columns[table_key]['links'] : 
				str_result += "MATCH (n1: DWTable {name:'"+table_key.split('.')[1]+"'}), (n2:DWTable {name:'"+link['target']+"'}) CREATE (n1)-[r:REFERENCES {on : '"+link['on']+"'}]->(n2);\n"

# Affichage des requêtes
print(str_result)
```
Ce script a été fait rapidement, et est donc entièrement optimisable (passer d'une complexité *3n* en *n* par exemple). C'est une base pour ceux qui voudront utiliser cette solution.

# III - Requêtage de notre solution
## A - Principe de requêtage Cypher
Pour faire une sélection, la syntaxe de base est `MATCH` suivi de la requête, puis d'un `RETURN` qui expose les résultats de la requête. À l'intérieur de la requête, il faut préciser des variables qui récupèreront les valeurs. 
On peut donc distinguer trois "méta-entités" : 
* **Les variables** : récupère les valeurs de l'exécution de la requête (dans notre premier exemple, c'est "n". Ce sont les variables que l'on retourne avec le `RETURN`
* **Les objets** : Se sont les types des noeuds ou relations que l'on requête. Dans notre cas, nous n'avons crée que des noeuds de type `DWTable` et des relations `references`, mais il serait tout à fait possible de créer d'autre objets (par exemple des noeuds `ConfigTable` ou des liens `isUsedBy` par exemple).
* **Les instances** : se sont les unité que l'on a fait des noeuds et des relations. Par exemple la table "Sample" est une instance de l'obet "DWTable".

Pour synthétiser, le but de la requête Cypher est de récupérer les instances d'objets dans des variables. 

Syntaxiquement parlant, on distingue aussi trois entités : 
* **Les termes Cypher** : ce sont les commandes qui donne la logique à appliquer au reste de la rquête (`MATCH`, `RETURN`, `WHERE` par exemple). 
* **La symbolisation des noeuds** : les noeuds sont symbolisés simplement minimalement par `()`, on peut ensuite ajouter des détails optionnels :  `(variable:Objet{<description JSON>})`
* **La symbolisation des relations** : Tout comme les noeauds, on décrit les liens minimalement par `--` et on peut le compléter avec `-[variable:Objet{<description JSON>}]-`. On peut aussi donner une direction à la liaison, simplement en ajoutant `<`ou `>` au début ou à la fin de la liaison. 


## B - Sélectionner tous les nœuds de type DWTable
Commençons simplement par sélectionner tous nos noeuds. Selon les principes énoncés plus tôt, voici donc notre première requête: 
```php
MATCH (n:DWTable) RETURN n
```
> **Énoncé de la requête** : "Cypher, récupère les instances de l'objet DWTable et mets les dans la variable n ; retourne moi ensuite la variable n"

## C - Sélectionner un nœud en particulier
Lors de leur création, nous avons fait en sorte que nos instances sont caractérisées par un identifiant unique et intelligible humainement qui est leur nom (les entités ont toute un id technique en réalité, mais il est complexe de les utiliser tels quels). 
Pour récupérer un noeud dont on connait le nom, on a juste à le préciser dans le match : 
```php
MATCH (n:DWTable {name:'Sample'}) 
RETURN n
```
Dans une autre mesure, on peut aussi utiliser la clause `WHERE` : 
```php
MATCH (n:DWTable) 
WHERE n.name = 'Sample' 
RETURN n
``` 
>**Énoncé de la requête** : "Cypher, récupère les instances de l'objets de DWTable <u>dont le nom est "Sample"</u> et mets les dans la variable n ; retourne moi ensuite la variable n"
 
## D - Sélectionner un nœud et ses connexions
Sélectionner un noeud particulier, nous savons le faire. Maintenant il nous faut récupérer ses noeurs connexes. Nous allons devoir faire appel à de nouvelles instances à stocker dans une nouvelle variable : 
```php
MATCH (n:DWTable {name:'Sample'})--(m) 
RETURN n, m
```
>**Énoncé de la requête** : "Cypher, récupère les instances de l'objets de DWTable dont le nom est "Sample" et mets les dans la variable n ; <u>récupère les instances liés à ce noeud et mets les dans la variable m</u> ;  retourne moi ensuite la variable n et m"

## E - Sélectionner les nœuds qui ont plus de 10 connexions
Après avoir vu comment on requêtait des noeuds, nous allons pouvoir commencer à requêter des relations. Pour cela, il nous faut utiliser un mot clef Cypher supplémentaire : `WITH`. 
Ce mot clef permet, entre autre, d'ajouter des fonctions d'agrégat à nos requêtes (à tout hasard, `count`, par exemple). 
A l'instar de la clause GROUP BY du SQL, il faut penser à bien préciser la clef de l'agrégation.
```php
MATCH 	(n:DWTable)-[r:references]-(:DWTable) 
WITH 	n, COUNT(r) as cpt 
WHERE 	cpt >= 10 
RETURN 	n,cpt
```
>**Énoncé de la requête** : "Cypher, récupère les instances de l'objets de DWTable et mets les dans la variable 'n' ; récupère les instances liés à ce noeud par le biais de relations que tu variabiliseras en 'r' ; pour chaque nœud initial de 'n', compte le nombre de relations 'r' qu'ils ont et alias le résultat en 'cpt' ;  retourne moi ensuite les variables 'n' et 'cpt' dont le compte est supérieur à 10".

## F - Sélectionner les nœuds qui ont 2 connexions ou plus avec le même nœud
Petite variante de la requête précédente : on veut récupérer les nœuds à l'origine et à la destination des relations multiples. Il nous faut donc récupérer ces destinations dans une variable et agréger en fonction des deux nœuds variabilisés. 
```php
MATCH	(n:DWTable)-[r:references]-(m:DWTable) 
WITH 	n, m, count(r) as cpt 
WHERE 	cpt >= 2 
RETURN 	n, m, cpt
```
>**Énoncé de la requête** : "Cypher, pour chaque DWTable 'n' liées à d'autres DWTables 'm', Compte le nombre de relations par couple 'n'<>'m'. Retourne moi les résultats dont le compte par paire de noeuds est supérieur ou égale à 2".

Fonctionnellement parlant, avec cette requête, on peut détecter les tables qui sont trop référencées plusieurs fois par la même table. On peut donc prendre des mesures en conséquences (mutualiser plusieurs clefs étrangères, enlever une contrainte qui était présente deux fois, etc.)

## G - Récupérer les noeuds distants de 2 relations d'un noeud
Pour cette requête, il faut introduire un nouvel élément : `*`. Cet élément indique une itération. On peut préciser le nombre d'itérations avec `*1..3` par exemple (de 1 à 3 fois). On peut ajouter cette clause à l'intérieur de la description d'un lien que l'on requête. Voyez plutôt : 
```php
MATCH (n:DWTable{name:'ReportableResult'})-[r*1..2]-(m:DWTable) 
RETURN n, m
```
>**Énoncé de la requête** : "Cypher, Pour la DWTable ReportableResult, récupère les noeuds DWTable qui sont reliés par 1 ou 2 relations. Variabilise la table ReportableResult en 'n' et les noeuds liés en 'm' ; retourne moi les variables n et m".

## H - Sélectionner le plus court chemin entre deux tables
Cette requête est une variante de la précédente, car il faut trouver un "plus court chemin". Ceci est trop complexe avec les outils natifs que nous avons pu avoir. On va donc avoir besoin d'une aide d'une fonction prédéfinie par Neo4J. Cette fonction est ShortestPath. 
On va devoir aussi récupérer un chemin dans nos noeuds. Pour cela il suffit d'affecter le résultat d'une clause de match à une variable (dans notre cas 'p') : 
```php
MATCH
	(s:DWTable {name:'Sample'}), 
	(rr:DWTable {name:'ReportableResult'}), 
	p = ShortestPath((s)-[:references*]-(rr)) 
RETURN p
```
>**Énoncé de la requête** : "Cypher, Pour la DWTable Sample variabilisée en s ; Pour la DWTable ReportableResult variabilisée en rr ; définit une variable 'p' comme étant : le plus court chemin entre le nœud 's' et 'rr', qui sont séparé de '*' liens. Retourne moi ensuite la variable 'p'".

Voyons ce que cette requête nous apporte ? On peut définir grâce à elle combien de jointure minimale il pourra y avoir pour relier ces deux tables, et selon leur volumétries, optimiser ces jointures. Grâce à ce résultat, on pourrait très bien refactoriser notre base afin d'ajouter une table de liaison spécifique. 

# IV - Conclusion
Maintenant vous pouvez visualiser vos schémas de BDD, et même mieux, interagir avec ! Gardons à l'esprit que cet article n'est qu'une "première main" sur le puissant outil qu'est Neo4J. Le langage Cypher comporte bien d'autre particularités qui le rende unique tant sur sa manière de l'écrire que ses temps de réponse ! 
Aussi, voyez plus loin que l'exemple d'utilisation qui a été fait avec cet article, par exemple remplacez les 'DWTables' par les fonctions et classes d'un code Java par exemple. Vous pourriez avoir un graph de l'impact des modification rapide, toujours à jour, et interactif ! 
