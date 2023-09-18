create schema nzoly;

use nzoly;


CREATE TABLE IF NOT EXISTS teams
(
TeamID INT auto_increment PRIMARY KEY NOT NULL,
TeamName VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS events
(
EventID INT auto_increment PRIMARY KEY NOT NULL,
EventName VARCHAR(80) NOT NULL,
Sport VARCHAR(50) NOT NULL,
NZTeam INT
);


CREATE TABLE IF NOT EXISTS members
(
MemberID INT auto_increment PRIMARY KEY NOT NULL,
TeamID INT NOT NULL,
FirstName VARCHAR(50) NOT NULL,
LastName VARCHAR(50) NOT NULL,
City VARCHAR(30),
Birthdate DATE NOT NULL,
FOREIGN KEY (TeamID) REFERENCES teams(TeamID)
ON UPDATE CASCADE
ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS event_stage
(
StageID INT auto_increment PRIMARY KEY NOT NULL,
StageName VARCHAR(50) NOT NULL,
EventID INT NOT NULL,
Location VARCHAR(50) NOT NULL,
StageDate DATE NOT NULL,
Qualifying BOOLEAN NOT NULL,
PointsToQualify float,
FOREIGN KEY (EventID) REFERENCES events(EventID)
ON UPDATE CASCADE
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS event_stage_results
(
ResultID INT auto_increment PRIMARY KEY NOT NULL,
StageID INT NOT NULL,
MemberID INT NOT NULL,
PointsScored float NOT NULL,
Position INT,
FOREIGN KEY (StageID) REFERENCES event_stage(StageID)
ON UPDATE CASCADE
ON DELETE CASCADE,
FOREIGN KEY (MemberID) REFERENCES members(MemberID)
ON UPDATE CASCADE
ON DELETE CASCADE
);


INSERT INTO Events VALUES (1,"Slopestyle","Snowboarding",101),
(3,"Big Air","Snowboarding",101),
(5,"Men's Halfpipe","Freestyle Skiing",103),
(6,"Men's 20 km individual biathlon","Biathlon",123),
(7,"Women's slopestyle","Freestyle Skiing",103),
(11,"Men's Halfpipe","Snowboarding",101);

INSERT INTO teams VALUES (101,"Snowboard"),
(103,"Freestyle Skiing"),
(123,"Biathlon"),
(102,"Alpine Skiing"),
(125,"Speed Skating");

INSERT INTO members VALUES (5629,103,"Ben","Barclay","Auckland","2002-02-04"),
(5630,103,"Anja","Barugh","Morrinsville","1999-05-21"),
(5631,103,"Finn","Bilous","Wanaka","1999-09-22"),
(5632,103,"Margaux","Hackett","Wanaka","1999-06-02"),
(5633,103,"Nico","Porteous","Hamilton","2001-11-23"),
(5634,101,"Zoi","Sadowski-Synnott","Wanaka","2001-03-06"),
(5635,101,"Tiarn","Collins","Queenstown","1999-11-09"),
(5636,125,"Peter","Michael","Wellington","1989-05-09"),
(5637,123,"Campbell","Wright","Rotorua","2002-05-25");

INSERT INTO event_stage VALUES
(356,"Heat 1",3,"Shougang","2022-02-14",TRUE,127.5),
(357,"Final",3,"Shougang","2022-02-15",FALSE, NULL),
(377,"Heat 1",1,"Genting Snow Park","2022-02-05",TRUE, 65.0),
(379,"Final",1,"Genting Snow Park","2022-02-06",FALSE, NULL),
(281,"Qualification",7,"Genting Snow Park","2022-02-14",TRUE, 63.40),
(289,"Qualification",11,"Genting Snow Park","2022-02-17",TRUE, 70.00),
(290,"Final",11,"Genting Snow Park","2022-02-19",FALSE, NULL);

INSERT INTO event_stage_results VALUES (467,356,5634,176.5,NULL),
(538,357,5634,177,2),(567,377,5634,86.75,NULL),(577,379,5634,92.88,1),
(265,281,5632,54.93,NULL),(222,289,5633,90.50,NULL),(223,290,5633,93,1);
