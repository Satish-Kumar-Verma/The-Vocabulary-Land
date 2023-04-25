CREATE SCHEMA PJ_Vocab;

USE PJ_Vocab;

CREATE TABLE Meaning
(
	M_Code VARCHAR(10) PRIMARY KEY,
    Word VARCHAR(45) NOT NULL,
    W_Meaning VARCHAR(250) NOT NULL
);

CREATE TABLE New_Word
(
	N_Code VARCHAR(10) PRIMARY KEY,
    M_Code VARCHAR(10),
    FOREIGN KEY (M_Code) REFERENCES Meaning (M_Code)
);

CREATE TABLE Known_Word
(
	KN_Code VARCHAR(10) PRIMARY KEY,
    M_Code VARCHAR(10),
    FOREIGN KEY (M_Code) REFERENCES Meaning (M_Code)
);

CREATE TABLE Bookmark_Word
(
	B_Code VARCHAR(10) PRIMARY KEY,
    M_Code VARCHAR(10),
    FOREIGN KEY (M_Code) REFERENCES Meaning (M_Code)
);

CREATE TABLE Favourite_Word
(
	FN_Code VARCHAR(10) PRIMARY KEY,
    M_Code VARCHAR(10),
    FOREIGN KEY (M_Code) REFERENCES Meaning (M_Code)
);

INSERT INTO Meaning
VALUE ('M_1', 'Hypothetical', 'Imagined or suggested but not necessarily real or true');

DELETE FROM Meaning WHERE M_Code = 'M_001';

ALTER TABLE meaning
MODIFY Word VARCHAR(45);

SET @temp = '';

SELECT M_Code INTO @temp FROM Meaning 
WHERE Word = 'Hypothetical';

INSERT INTO Favourite_Word
VALUE ('F_1', @temp);

DELETE FROM Favourite_Word WHERE FN_Code = 'F_1';


INSERT INTO Meaning
VALUES ('M_2', 'temp', 'Justtemp'),
		('M_3', 'temp1', 'Justtemp1');
        
DELETE FROM Meaning WHERE M_Code = 'M_3';     



SET @tp = 0;

SELECT COUNT(M_Code) INTO @tp FROM Meaning;
select @tp;  


show COLUMNS from PJ_Vocab.meaning;

USE PJ_Vocab;


DELIMITER //

-- P_ID = B_Code, D_ID = M_Code  (eg)

Create procedure check_bookmark(IN word_input varchar(45), OUT output_var bool)
BEGIN
    DECLARE W_ID VARCHAR(10);
    SET @temp = "";
    
    SELECT M_Code INTO W_ID FROM PJ_Vocab.meaning WHERE word = word_input;
    
    SELECT M_Code INTO @temp FROM bookmark_word WHERE M_Code = W_ID;
    
    IF @temp = "" THEN
		SET output_var = true;
    ELSE 
		SET output_var = false;
        
	END IF;
END //

DELIMITER ;


DELIMITER //

-- P_ID = B_Code, D_ID = M_Code  (eg)

Create procedure check_favourite(IN word_input varchar(45), OUT output_var bool)
BEGIN
	DECLARE W_ID VARCHAR(10);
    SET @temp = "";
    
    SELECT M_Code INTO W_ID FROM PJ_Vocab.meaning WHERE word = word_input;
    SELECT M_Code INTO @temp FROM favourite_word WHERE M_Code = W_ID;
    
    IF @temp = "" THEN
		SET output_var = true;
    ELSE 
		SET output_var = false;
        
	END IF;
END //

DELIMITER ;



DELIMITER //

-- P_ID = B_Code, D_ID = M_Code  (eg)

Create procedure check_known(IN word_input VARCHAR(45), OUT output_var bool)
BEGIN
	DECLARE W_ID VARCHAR(10);
    SET @temp = "";
    
    SELECT M_Code INTO W_ID FROM PJ_Vocab.meaning WHERE word = word_input;
    SELECT M_Code INTO @temp FROM known_word WHERE M_Code = W_ID;
    
    IF @temp = "" THEN
		SET output_var = true;
    ELSE 
		SET output_var = false;
        
	END IF;
END //

DELIMITER ;


DELIMITER //

-- P_ID = B_Code, D_ID = M_Code  (eg)

Create procedure check_new(IN word_input varchar(45), OUT output_var bool)
BEGIN
	DECLARE W_ID VARCHAR(10);
    SET @temp = "";
    
    SELECT M_Code INTO W_ID FROM PJ_Vocab.meaning WHERE word = word_input;
    SELECT M_Code INTO @temp FROM new_word WHERE M_Code = W_ID;
    
    IF @temp = "" THEN
		SET output_var = true;
    ELSE 
		SET output_var = false;
        
	END IF;
END //

DELIMITER ;



drop procedure check_favourite;
drop procedure check_known;
drop procedure check_new;


SELECT Word, W_Meaning FROM meaning WHERE M_Code IN 
(
	SELECT M_Code FROM bookmark_word
) order by Word ASC LIMIT 3;





