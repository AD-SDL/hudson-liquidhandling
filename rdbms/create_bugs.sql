create database if not exists test_bugs;


use test_bugs;

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
 * COLUMNS:     plate_id	A Unique identifier for the plate
 *              type		The type of plate:
					assay
					source
 *      	process_status  Where the plate is in the sequencing process
 *		barcode		barcode for the plate
 *		name		name string for the plate
 *		format    	The number of wells (96 or 384). MUST NOT BE NULL.
 *		origin	  	The original source: pgf, lanl, llnl...
 *
 *------------------------------------------------------------------------------*/

create table plate
(
 plate_id       int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
 type     	VARCHAR(30),
 process_status VARCHAR(10) default 'new',
 barcode 	VARCHAR(255) unique,
 name 		VARCHAR(255),
 format   	int(9),
 origin	  	VARCHAR(10)
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
 *
 *------------------------------------------------------------------------------*/

create table source_plate
(
 plate_id       	int(11),
 type			varchar(24),
 well			varchar(10),
 location_serial_num    int(11)    ,
 availability   	VARCHAR(10),
 name			VARCHAR(256)
);


/*------------------------------------------------------------------------------
 *
 * TABLENAME	assay_plate
 * FUNCTION	THe plates containing a treatment condition being measured
 *		Think AMR, it's the plate that we take absorbance readings on.
 * COLUMNS
 * 	type	The type of assay, for example dose_response
 *      well	The well id
 *      sample  The sample in the well, ideally comes from the source plate and
 *              is an ID, but for now we'll just use the sample name.
 *	value	the measured value for that well
*------------------------------------------------------------------------------*/

create table assay_plate
(
	plate_id	int(11),
	type		varchar(24),
	well		varchar(10),
	sample		varchar(256),
	value		float
);
