PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('a360a4b44062');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	role VARCHAR NOT NULL, 
	password VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
INSERT INTO users VALUES(1,'baileysmith','wdavis@example.com','Employer','$2b$12$Y4HXsVQOhRYmn30wvvtu/uR6wUWJzFIUfp0N82akgTxjSAMpkmA.G');
INSERT INTO users VALUES(2,'brian15','trujillochristine@example.com','Job Seeker','$2b$12$s2.DUqtSlQ/Yuig1/CZ1k.EAj8fMj6hK.lKJBlTtXXp2N6Ba.OIZC');
INSERT INTO users VALUES(3,'jarvisashley','muellerrichard@example.com','Job Seeker','$2b$12$4QzjW/zN/cPGEGJXvj1EU.9q3ptqCT6ZJY9CAKD7M3BDZMNkH97Bi');
INSERT INTO users VALUES(4,'josephrodriguez','kayla87@example.net','Job Seeker','$2b$12$c2lY5xY9EF1yspIoyT35xOwlbKqHGtUPK10a4K3O9w2Rh3Owb8fzu');
INSERT INTO users VALUES(5,'johnsmith','kjohnson@example.com','Employer','$2b$12$mY5HqHRagCArNJNAg9h4Y.sm5PZf52sLT8Z36DhFNS8wkZcSJSwq6');
INSERT INTO users VALUES(6,'jomo','jomo@gmail.com','jobseeker','$2b$12$RhsqVlKtOvrkp5LMrxLThOwQAOdmlgcSnizVnVvTLro2Rie8Omq.O');
INSERT INTO users VALUES(7,'sharon','sharon@example.com','jobseeker','$2b$12$YHBF.FAS15gd36InzTZVJeSoudfj5GApnC1GA9oyNEdRyVePYDfPq');
INSERT INTO users VALUES(8,'wambui','wambui@example.com','employer','$2b$12$mZhfdyv.VxSEHaclzw3BluVOhW.jbp3cK7zefL7yaFS8wf9e4YxGS');
CREATE TABLE jobs (
	id INTEGER NOT NULL, 
	title VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	location VARCHAR NOT NULL, 
	company VARCHAR NOT NULL, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO jobs VALUES(1,'Archaeologist','Statement then painting drug human safe seem. Lot room remain. Against speech so.','East Andreaburgh','Ramos-Mendoza',5);
INSERT INTO jobs VALUES(2,'Nurse, children''s','Beat before others difference stop citizen. Skin onto turn finish. Improve trip foot suddenly free. Various policy smile growth.','Jimenezberg','Nielsen, Green and Vaughn',1);
INSERT INTO jobs VALUES(3,'Science writer',replace('His five finish story. Nice this job may.\nImportant maybe offer recent section yard. Car economy through hour act. Model style travel either moment big.','\n',char(10)),'Wongchester','Quinn-Shelton',4);
INSERT INTO jobs VALUES(4,'Proofreader',replace('Officer next dog. Feel about always call price water similar. Speak level big plan.\nEnough movie behavior bag role common. South public project city run recognize his.','\n',char(10)),'Greenechester','Gardner, Bauer and Rodriguez',3);
INSERT INTO jobs VALUES(5,'Embryologist, clinical',replace('Rich they seek force. Ground kitchen inside article but water.\nBorn pay unit size third. Computer exist network necessary dog.\nMoney level truth success able decide. Discuss her real nice really.','\n',char(10)),'South Andrew','Trevino, Reyes and Patterson',2);
INSERT INTO jobs VALUES(6,'Financial risk analyst',replace('Line somebody safe so various share sister. Else attention analysis plant man fish.\nPart dog PM sort message score seek. Consider picture seven around expert.\nTheir red only with choose.','\n',char(10)),'Robertchester','Davis Group',4);
INSERT INTO jobs VALUES(7,'Engineer, building services',replace('Shoulder be public life enough throughout surface. Tv about oil teacher themselves couple.\nProject coach positive radio have capital. Project car official different machine idea inside.','\n',char(10)),'Allenmouth','Mason, Mcintyre and Franklin',5);
INSERT INTO jobs VALUES(8,'Firefighter',replace('Thing expect mother site customer candidate. Study catch people possible.\nDown brother beyond year maybe enjoy. Happy region issue.\nRun bring quality evidence blood. Charge into cultural ever let.','\n',char(10)),'Lake Gloria','Noble LLC',2);
INSERT INTO jobs VALUES(9,'Software Engineering','We’re looking for a passionate Software Engineer to design, build, and maintain scalable web applications. You’ll collaborate with cross-functional teams, write clean and efficient code, and contribute to the full software development lifecycle.','Riverton, Westlake','TechNova Solutions',8);
CREATE TABLE applications (
	id INTEGER NOT NULL, 
	status VARCHAR NOT NULL, 
	cover_letter VARCHAR, 
	user_id INTEGER NOT NULL, 
	job_id INTEGER NOT NULL, name VARCHAR, email VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(job_id) REFERENCES jobs (id)
);
INSERT INTO applications VALUES(1,'rejected','Past receive fight. Foreign should cause civil leave. Tonight discover plant economy community board.',3,4,NULL,NULL);
INSERT INTO applications VALUES(2,'pending','Government lot style training prove effort including loss. Difference ten who political protect place.',2,8,NULL,NULL);
INSERT INTO applications VALUES(3,'rejected','Base before TV end management charge half. Thus thing if national training will every. Purpose consumer however consumer.',3,2,NULL,NULL);
INSERT INTO applications VALUES(4,'pending','Gas sense goal poor. Like build career window scientist threat record. Player paper ever watch some within. Admit professional clearly but wear.',2,8,NULL,NULL);
INSERT INTO applications VALUES(5,'accepted','Single notice Mrs rate fine hot.',2,6,NULL,NULL);
INSERT INTO applications VALUES(6,'pending','Teach catch wife to as opportunity. Spend break fly huge key reason hit management. Test hot main.',4,5,NULL,NULL);
INSERT INTO applications VALUES(7,'rejected','Avoid reveal mother assume artist buy.',1,5,NULL,NULL);
INSERT INTO applications VALUES(8,'pending','Performance table serious necessary. Politics across hour. Fear position rule people drug affect.',4,5,NULL,NULL);
INSERT INTO applications VALUES(9,'rejected','At movie responsibility mind. Successful establish baby major east rock green attack. Court star animal far vote identify.',4,4,NULL,NULL);
INSERT INTO applications VALUES(10,'rejected','Here artist despite last also husband growth. Hotel leave throw policy economy involve.',2,6,NULL,NULL);
INSERT INTO applications VALUES(11,'pending','Three dog yeah guess. Situation here develop structure hair production office.',2,6,NULL,NULL);
INSERT INTO applications VALUES(12,'pending','Structure daughter example quite society. Really almost data difficult probably.',1,4,NULL,NULL);
INSERT INTO applications VALUES(13,'accepted','Weight she sing condition. Purpose boy measure job. Human last night nation analysis how. Different space whose water travel trouble score town.',1,2,NULL,NULL);
INSERT INTO applications VALUES(14,'accepted','Decision full report share. Push attention very movement.',3,1,NULL,NULL);
INSERT INTO applications VALUES(15,'rejected','Turn shoulder stand nor case include Congress. Account face anything door while run.',3,8,NULL,NULL);
INSERT INTO applications VALUES(16,'pending','Excited to start',1,1,'Sharonn','sharonn@example.com');
INSERT INTO applications VALUES(17,'pending','Looking forward to join your company.',8,9,NULL,NULL);
COMMIT;
