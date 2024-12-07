 -- Get total column count
SELECT 
   'GRAND TOTAL' AS MetricName,
   (
       SELECT COUNT(c.name)
       FROM sys.objects obj
       INNER JOIN sys.columns c ON obj.object_id = c.object_id
       WHERE obj.type IN ('U', 'V')
   ) AS TotalColumnsInDatabase,
   (
       SELECT COUNT(c.name)
       FROM sys.objects obj
       INNER JOIN sys.columns c ON obj.object_id = c.object_id
       LEFT JOIN sys.extended_properties ep ON ep.major_id = obj.object_id 
           AND ep.minor_id = c.column_id 
           AND ep.name = 'MS_Description'
       WHERE obj.type IN ('U', 'V')
       AND ep.value IS NOT NULL
   ) AS ColumnsWithDescriptions,
   (
       SELECT COUNT(c.name)
       FROM sys.objects obj
       INNER JOIN sys.columns c ON obj.object_id = c.object_id
       LEFT JOIN sys.extended_properties ep ON ep.major_id = obj.object_id 
           AND ep.minor_id = c.column_id 
           AND ep.name = 'MS_Description'
       WHERE obj.type IN ('U', 'V')
       AND ep.value IS NULL
   ) AS ColumnsWithoutDescriptions