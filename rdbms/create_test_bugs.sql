create database if not exists test_bugs;

use test_bugs;

CREATE TABLE experiment (
     experiment_id int(11) NOT NULL AUTO_INCREMENT,
     project_id int(11),
     PRIMARY KEY (experiment_id)
);
alter table experiment add CONSTRAINT project_fk FOREIGN KEY (project_id) REFERENCES project(project_id);


/*------------------------------------------------------------------------------
 *
 * TABLENAME    PROJECT
 *
 * FUNCTION     The current organism being finished
 *
 * COLUMNS:     project_id   		Unique identifier for the project
 *		main_project_id		If this is a subproject, the id of the main
 * 					project it is associated with another project.
 *              name         		The short name of the project (used to name files, ...)
 *              full_name    		The full name for the project (human interpertable)
 *		type 			An enumerated set, descriptive of the project type
 *
 *------------------------------------------------------------------------------*/

create table project
(
 project_id		int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
 main_project_id	INT,
 name			VARCHAR(255) ,
 full_name		VARCHAR(255),
 type			VARCHAR(10),
 start_date		DATE,
 finish_date		DATE
);


/*------------------------------------------------------------------------------
 *
 * TABLENAME    PLATE
 *
 * FUNCTION     A physical plate of any kind.
 *
 * COLUMNS:     Inc_ID	A Unique identifier for the plate
 *              type		The type of plate:
					assay
					source
 *      	process_status  Where the plate is in the sequencing process
 *		barcode		barcode for the plate
 *		Exp_ID		Experiment ID (Curently file name)
 *		format    	The number of wells (96 or 384). MUST NOT BE NULL.
 *		Date_created 	First recording date of the plate information
 *		Time_created 	First recording time of the plate information
 *		Control_QC      Either "Pass" or "Fail".
 *      	Exp_Image       Experiment image in BLOB format
 *              Name		name string for the plate
 *		Origin  	The original source: hope, cdc, ...
 *
 *------------------------------------------------------------------------------*/

create table plate
(
 Inc_ID       int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
 Type     	VARCHAR(30),
 Process_status VARCHAR(15) default 'New',
 Barcode 	VARCHAR(255),
 Exp_ID 	        VARCHAR(255) NOT NULL,
 Format   	int(9),
 Date_created	VARCHAR(50),
 Time_created 	VARCHAR(50),
 Z_Score_QC VARCHAR(15),
 Exp_Image	mediumblob,
 Name 		VARCHAR(255),
 Origin	  	VARCHAR(25)

);

/*------------------------------------------------------------------------------
 *
 * TABLENAME    PLATE_QUALITY
 *
 * FUNCTION     Tracks the quality for each plate.
 *
 * COLUMNS:     plate_id           References a record in the plate table
 *              type	           The type of quality being tracked
 *              value		   The quality value
 *
 *
 *------------------------------------------------------------------------------*/

create table plate_quality
(
 plate_id           int(11),
 type 		    VARCHAR(10),
 value		    VARCHAR(255)
);

/*------------------------------------------------------------------------------
 * Incomplete
 * TABLENAME    SOURCE_PLATE
 *
 * FUNCTION     The plates containing libraries of dna to be used in
 *              finishing a project.
 *
 * COLUMNS:     plate_id     	Unique identifier for this plate
 *		type		the type of source plate
 *              well		the well id
 *		location_serial_num
 *              availability  	Indicates status of the plate - available, unusable...
 *
 * PLATE TYPES = ('strain_collection', )
 *		strain_collection represents a bacteria strain library.
 *
 * AVAILABILTY = ('available', 
 *		available indicates that the plate is available for use.
 *
 *------------------------------------------------------------------------------*/

create table source_plate
(
 plate_id       	int(11),
 type			varchar(24),
 well			varchar(10),
 sample_id		varchar(100),
 location_serial_num    int(11),
 availability   	VARCHAR(10),
 name			VARCHAR(256)
);
alter table source_plate add constraint plate_fk_1 foreign key (plate_id) references plate(plate_id);

/*------------------------------------------------------------------------------
 *
 * TABLENAME	assay_plate
 * FUNCTION	The plates containing a treatment condition being measured
 *		Think AMR, it's the plate that we take absorbance readings on.
 * COLUMNS
 *		Data_group	Group of the data (Experimental or Control)
 *		Row_num 	Row number for indexing 
 *      well	The well id
 *		Raw_Value 		Raw value
 *		Elapsed_time	Readings at different timepoints
 *		Data_File_Name	Experiment data file name
 *		Reading_date	Plate reading date
 *		Reading_time	Plate reading time
 *		Assay_Details 	Details of the assay. For example Raw OD(590)
 *		Blank_Adj_Value
 * 		type	The type of assay, for example dose_response
 *      sample  The sample in the well, ideally comes from the source plate and
 *              is an ID, but for now we'll just use the sample name.
 *		value	the measured value for that well
*------------------------------------------------------------------------------*/


create table assay_plate
(
 Inc_ID	int(11) NOT NULL,
 Data_group	varchar(50),
 Row_num	int(11),
 Well		varchar(10),
 Raw_Value	varchar(256),
 Elapsed_time varchar(50),
 Data_File_Name varchar(256),
 Reading_date	varchar(50),
 Reading_time	varchar(50),
 Assay_Details	 varchar(100),
 Blank_Adj_Value	 varchar(100),
 Type		varchar(50),
 Sample		varchar(256),

);
alter table assay_plate add constraint plate_fk_2 foreign key (plate_id) references plate(plate_id);

create table Test_plate
(
 Inc_ID       int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
 Type     	VARCHAR(30),
 Process_status VARCHAR(15) default 'New',
 Barcode 	VARCHAR(255),
 Exp_ID 	        VARCHAR(255) NOT NULL,
 Format   	int(9),
 Date_created	VARCHAR(50),
 Time_created 	VARCHAR(50),
 Z_Score_QC VARCHAR(15),
 Exp_Image	mediumblob,
 Name 		VARCHAR(255),
 Origin	  	VARCHAR(25)

);

create table Test_assay_plate
(
 Inc_ID	int(11) NOT NULL,
 Data_group	varchar(50),
 Row_num	int(11),
 Well		varchar(10),
 Raw_Value	varchar(256),
 Elapsed_time varchar(50),
 Data_File_Name varchar(256),
 Reading_date	varchar(50),
 Reading_time	varchar(50),
 Assay_Details	 varchar(100),
 Blank_Adj_Value	 varchar(100),
 Type		varchar(50),
 Sample		varchar(256),

);

/*------------------------------------------------------------------------------
 *
 * TABLENAME    source_sample_alias
 * FUNCTION     Provides aliases for a sample in a source plate. The alias is
 *		another name for the sample_id in the source plate.
 * COLUMNS
 *              sample_id varchar(100),
 *              alias varchar(100),
 *		alias_type varchar(64),
 *		constraint  sample_id_alias_constraint UNIQUE (sample_id, alias, alias_type)
 *              value   the measured value for that well
 *
 * ALIAS_TYPES = ('PATRIC_GENOME', )
 *		PATRIC_GENOME is a genome id in the PATRIC database
*------------------------------------------------------------------------------*/

create table source_sample_alias (
	sample_id varchar(100),
	alias varchar(100),
	alias_type varchar(64),
	constraint  sample_id_alias_constraint UNIQUE (sample_id, alias, alias_type)
);
