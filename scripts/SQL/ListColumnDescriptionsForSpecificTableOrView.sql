
-- replace the database name with the name of the database you want to query
DECLARE @ObjectName NVARCHAR(100) =  'YOUR-TABLE-OR-VIEW-NAME';

SELECT @ObjectName = name 
FROM sys.objects 
WHERE name = @ObjectName;

IF @ObjectName IS NULL
   PRINT 'Object not found'
ELSE
BEGIN
   DECLARE @ColumnInfo NVARCHAR(MAX)
   
   DECLARE column_cursor CURSOR FOR 
   SELECT 
       CONCAT(
           c.name,
           ' | Type: ',
           TYPE_NAME(c.user_type_id),
           CASE 
               WHEN TYPE_NAME(c.user_type_id) IN ('varchar', 'nvarchar', 'char', 'nchar') 
               THEN '(' + 
                   CASE 
                       WHEN c.max_length = -1 THEN 'MAX'
                       WHEN TYPE_NAME(c.user_type_id) IN ('nvarchar', 'nchar') THEN CAST(c.max_length/2 AS VARCHAR(10))
                       ELSE CAST(c.max_length AS VARCHAR(10))
                   END + ')'
               ELSE ''
           END,
           ' | Description: ',
           CONVERT(NVARCHAR(MAX), ISNULL(ep.value, 'No description available'))
       )
   FROM 
       sys.objects obj
       INNER JOIN sys.columns c ON obj.object_id = c.object_id
       LEFT JOIN sys.extended_properties ep ON ep.major_id = obj.object_id 
           AND ep.minor_id = c.column_id 
           AND ep.name = 'MS_Description'
   WHERE 
       obj.type IN ('U', 'V')
       AND obj.name = @ObjectName
   ORDER BY 
       c.column_id;

   OPEN column_cursor
   FETCH NEXT FROM column_cursor INTO @ColumnInfo

   WHILE @@FETCH_STATUS = 0
   BEGIN
       PRINT @ColumnInfo
       FETCH NEXT FROM column_cursor INTO @ColumnInfo
   END

   CLOSE column_cursor
   DEALLOCATE column_cursor
END