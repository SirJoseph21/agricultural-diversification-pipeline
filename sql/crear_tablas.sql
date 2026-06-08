USE agricola_clima;

SELECT 'categoria_cultivo' AS tabla, COUNT(*) AS registros FROM categoria_cultivo
UNION ALL
SELECT 'cultivos',                   COUNT(*)                FROM cultivos
UNION ALL
SELECT 'estados',                    COUNT(*)                FROM estados;