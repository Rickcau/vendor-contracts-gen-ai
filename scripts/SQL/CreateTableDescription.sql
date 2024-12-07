-- First check if the description exists
IF EXISTS (
    SELECT 1 
    FROM sys.extended_properties 
    WHERE [major_id] = OBJECT_ID('dbo.Contracts')
        AND [name] = N'MS_Description'
        AND [minor_id] = 0
)
BEGIN
    -- Update if it exists
    EXEC sp_updateextendedproperty 
        @name = 'MS_Description', 
        @value = 'Contracts, Addendums, Amendments between vendors and clients.',
        @level0type = 'SCHEMA', 
        @level0name = 'dbo', 
        @level1type = 'TABLE', 
        @level1name = 'Contracts';
END
ELSE
BEGIN
    -- Add if it doesn't exist
    EXEC sp_addextendedproperty 
        @name = 'MS_Description', 
        @value = 'Contracts, Addendums, Amendments between vendors and clients.',
        @level0type = 'SCHEMA', 
        @level0name = 'dbo', 
        @level1type = 'TABLE', 
        @level1name = 'Contracts';
END