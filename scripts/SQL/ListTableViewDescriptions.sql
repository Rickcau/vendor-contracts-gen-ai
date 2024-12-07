-- replace the database name with the name of the database you want to query
USE [YOUR-DB];
 
WITH ObjectInfo AS (
    -- Get Tables
    SELECT 
        t.name AS ObjectName,
        t.object_id,
        s.name AS SchemaName,
        'Table' AS ObjectType
    FROM sys.tables t
    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
    
    UNION ALL
    
    -- Get Views
    SELECT 
        v.name AS ObjectName,
        v.object_id,
        s.name AS SchemaName,
        'View' AS ObjectType
    FROM sys.views v
    INNER JOIN sys.schemas s ON v.schema_id = s.schema_id
)
SELECT 
    o.ObjectName,
    o.SchemaName,
    o.ObjectType,
    COALESCE(ep.value, 'No description available') AS ObjectDescription
FROM ObjectInfo o
LEFT JOIN sys.extended_properties ep ON 
    ep.major_id = o.object_id AND 
    ep.minor_id = 0 AND 
    ep.name = 'MS_Description'
ORDER BY 
    o.ObjectType,
    o.SchemaName, 
    o.ObjectName;