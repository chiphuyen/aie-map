PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE books (
	id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	short_name VARCHAR(10) NOT NULL, 
	pin_color VARCHAR(7) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (short_name)
);
INSERT INTO books VALUES(1,'AI Engineering','AIE','#FF0000');
INSERT INTO books VALUES(2,'Designing Machine Learning Systems','DMLS','#00FF00');
CREATE TABLE reviews (
	id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	city_id INTEGER NOT NULL, 
	review_text TEXT, 
	reviewer_name VARCHAR(255), 
	company VARCHAR(255), 
	role VARCHAR(255), 
	review_date DATE, 
	created_at DATETIME, 
	original_post_url TEXT, 
	screenshot_path VARCHAR(500), 
	source VARCHAR(255), social_media_url TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(book_id) REFERENCES books (id), 
	FOREIGN KEY(city_id) REFERENCES cities (id)
);
INSERT INTO reviews VALUES(1,1,1,'With recent advancements in Al, I anticipated more automated annotation and analysis. Chip Huyen, in "Al Engineering," discusses the potential of training models with genome sequences, noting proprietary data as a common limitation.','Daniel P Vaughan','Mastercard','Director, Software Engineering','2025-06-10','2025-06-10 13:29:06.104631','https://www.linkedin.com/feed/update/urn:li:activity:7338134275457789954/',NULL,'LinkedIn',NULL);
INSERT INTO reviews VALUES(2,2,2,replace('Just started reading Designing Machine Learning Systems by Chip Huyen\n\nBeen wanting to dive deeper into the practical side of ML, and this book came highly recommended by folks who''ve actually deployed at scale. Chapter 1 already reshaped how I think about ML systems.\n\n🔍 Key takeaways from Chapter 1 – “Overview of ML Systems”:\n\n- ML isn’t always the answer — rule-based systems can be simpler and more effective.\n- Real-world ML is messy: shifting data, latency issues, and stakeholder trade-offs are the norm.\n- Think systems, not just models — algorithms are only a small piece of the puzzle.\n- Success = Model + Deployment + Monitoring + Retraining + Business Alignment.\n\n🛠️ How I’m applying this:\n\nThis gave me a fresh perspective on my own projects. I’m going to start thinking about why I’m building something, not just how — and make sure I consider things like maintainability and monitoring from day one.\n','\n',char(10)),'Tharun Kammavarambatti','Illinois Institute of Technology, Chicago','Student','2025-06-09','2025-06-10 13:32:56.479002','',NULL,'LinkedIn','');
INSERT INTO reviews VALUES(3,1,3,replace('This jewel arrived Friday morning. It''s helping me understand the “why” of LLMs, not just the code-centric “how”.\n\nChapter 3 on evaluation is, TBH, scary. I came from a semiconductor background and got nervous when my verification colleagues had to make judgment calls.\n\nProps to for an excellent resource.\n','\n',char(10)),'Brian Piercy','AMD',' Program Manager ','2025-06-03','2025-06-10 20:36:33.837409','https://www.linkedin.com/posts/brianpiercy_this-jewel-arrived-friday-morning-its-helping-activity-7334961377452720129-G7MX?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAIQAJQBE3ykLNnsOPVvxwuuVCOir2zAjOQ',NULL,'LinkedIn','');
INSERT INTO reviews VALUES(4,1,4,replace('The ROI as a software engineer wanting to work at a startup (or YC startup) for picking up Al Engineeing by @chipro plus building a few side\nprojects using LLMs is massive right now.\n','\n',char(10)),'Gergely Orosz','The Pragmatic Engineer','Engineer','2025-06-08','2025-06-11 10:42:49.631726','https://x.com/GergelyOrosz/status/1932054321836749054',NULL,'X','https://x.com/GergelyOrosz');
INSERT INTO reviews VALUES(5,1,5,'This is literally the gold standard playbook for building AI apps','Aadit Sheth','Neatprompts','CEO','2025-04-26','2025-06-11 11:42:14.715460','',NULL,'X','https://x.com/aaditsh');
INSERT INTO reviews VALUES(6,1,6,replace('every day that goes by without reading this gold book is a loss, just look at the topics:\n\n> building Al apps with LLMs\n\n> understanding foundational models\n\n> evaluating Al systems and metrics\n\n> RAG & Agents\n\n> dataset engineering\n','\n',char(10)),'ℏεsam','','','2025-04-25','2025-06-11 11:44:23.164839','https://x.com/Hesamation/status/1915861138807341122',NULL,'CAMEL-AI.org','https://x.com/Hesamation');
INSERT INTO reviews VALUES(7,1,7,replace('Al Engineering by Chip Huyen\n\nIt''s an awesome resource for learning how to develop Al applications.\n','\n',char(10)),'Matt Dancho','Business Science','Founder','2025-03-31','2025-06-11 12:39:14.843389','https://x.com/mdancho84/status/1906694869671633301',NULL,'X','https://x.com/mdancho84');
INSERT INTO reviews VALUES(8,1,10,'I have a copy of Chip Huyen''s "Al Engineering" on my desk at all times. My team and I probably reference it daily. The parts of agentic Al and inference optimization are particularly compelling.','Ashley Nicholson','Avenir Technology','CEO','2025-06-11','2025-06-11 21:06:33.656916','https://www.linkedin.com/feed/update/urn:li:activity:7338617165849223173?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7338617165849223173%2C7338668131931901954%29&dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287338668131931901954%2Curn%3Ali%3Aactivity%3A7338617165849223173%29',NULL,'LinkedIn','https://www.linkedin.com/in/ashley%2D%2Dnicholson/');
INSERT INTO reviews VALUES(9,2,12,'Totally agree on Chip Huyen’s Designing ML Systems — it bridges the gap between theory and production beautifully.','Meiyu Wen','Mashang Consumer Finance','Senior Machine Learning Engineer','2025-06-13','2025-06-13 09:12:46.694852','https://www.linkedin.com/feed/update/urn:li:activity:7339199843124310016?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7339199843124310016%2C7339202766977794048%29&dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287339202766977794048%2Curn%3Ali%3Aactivity%3A7339199843124310016%29',NULL,'LinkedIn','https://www.linkedin.com/in/meiyuwen-2b28bb18b/');
INSERT INTO reviews VALUES(10,1,13,replace('This is excellent - crammed with practical advice about how to build\nuseful systems that use LLMs to run tools in a loop to achieve a goal.\n\nThe article is adapted from Chip''s brand new O''Reilly book AI Engineering. I think this is an excellent advertisement for the book itself.','\n',char(10)),'Simon Willison','Django','Creator','2025-01-11','2025-06-13 09:35:57.916880','https://x.com/simonw/status/1878138024292421835',NULL,'X','https://x.com/simonw');
CREATE TABLE review_assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_id INTEGER NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_name VARCHAR(255),
                    file_type VARCHAR(50),
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
                );
CREATE TABLE IF NOT EXISTS "cities" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    country VARCHAR(255) NOT NULL,
                    state VARCHAR(255),
                    latitude DECIMAL(10, 8) NOT NULL,
                    longitude DECIMAL(11, 8) NOT NULL,
                    UNIQUE(name, country, state)
                );
INSERT INTO cities VALUES(1,'London','The UK',NULL,51.4955416000000028,-0.1278582000000000051);
INSERT INTO cities VALUES(2,'Chicago','United States',NULL,41.8755615999999975,-87.62442120000000045);
INSERT INTO cities VALUES(3,'Charleston','United States',NULL,38.34982000000000113,-81.63262000000000284);
INSERT INTO cities VALUES(4,'Amsterdam','Netherlands',NULL,52.37402999999999765,4.88968999999999987);
INSERT INTO cities VALUES(5,'San Francisco','United States',NULL,37.77492999999999768,-122.4194200000000023);
INSERT INTO cities VALUES(6,'Bologna','Italy',NULL,44.49381000000000342,11.33874999999999921);
INSERT INTO cities VALUES(7,'Pittsburgh','United States',NULL,40.44062000000000268,-79.99589000000000282);
INSERT INTO cities VALUES(8,'Washington','United States',NULL,37.13054000000000344,-113.5082900000000023);
INSERT INTO cities VALUES(9,'Springfield','United States',NULL,44.04623999999999739,-123.0220300000000008);
INSERT INTO cities VALUES(10,'Washington','United States','District of Columbia',38.89511000000000251,-77.03637000000000513);
INSERT INTO cities VALUES(12,'Beijing','China',NULL,39.90749999999999887,116.3972299999999934);
INSERT INTO cities VALUES(13,'San Francisco','United States','California',37.77492999999999768,-122.4194200000000023);
CREATE TABLE admin_sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45)
                );
INSERT INTO admin_sessions VALUES('9rzIojIkOs-veraXUnXYFKVLRD3Z0UFpNJqbMgrmqsM','2025-06-14 06:25:29.268641','2025-06-13 06:25:29.270022','2025-06-13 06:25:29.270023','127.0.0.1');
INSERT INTO admin_sessions VALUES('7E7zACFA3_btUxlJRFr4KnR4nsw1CvQhg8OaiqNRIUU','2025-06-14 06:37:47.596709','2025-06-13 06:37:47.598410','2025-06-13 06:37:47.598411','127.0.0.1');
INSERT INTO admin_sessions VALUES('ofQFTntTcPMVFX3IWem_zL3p5xlrtFxFrvJxKAwiWew','2025-06-14 07:01:20.716685','2025-06-13 07:01:20.717766','2025-06-13 07:01:20.717767','127.0.0.1');
INSERT INTO admin_sessions VALUES('TRphFW2Acui1MqqDlkJqLXrIHcMyvYcqxL2fo7fm1Us','2025-06-14 07:05:59.175652','2025-06-13 07:05:59.176705','2025-06-13 10:01:24.794593','127.0.0.1');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('cities',13);
CREATE INDEX ix_books_id ON books (id);
CREATE INDEX ix_reviews_id ON reviews (id);
COMMIT;
