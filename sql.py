# 3rd party
import pyodbc


def db_conn():
    conn = pyodbc.connect(
        '''
        Driver={ODBC Driver 17 for SQL Server};
        Server=;
        Database=DMT;
        Trusted_Connection=yes;
        '''
    )
    cursor = conn.cursor()
    return cursor


promos_sql = (
    '''
    SELECT DISTINCT c.CampaignId AS 'Campaign ID'
        , CASE WHEN rr2.check_value = 1 THEN c.Notes
            ELSE prod.name
            END AS 'Product'
        , loc.name AS 'Location'
        , CASE
            WHEN loc.name = 'Add-Ons' THEN 'Explore Add-Ons'
            WHEN loc.name = 'Free' THEN 'Explore Free'
            WHEN c.title LIKE '% big %'
                AND loc.name IN ('Video Games', 'What''s Hot')
                THEN 'Large Banner'
            WHEN c.title LIKE '%games eg%'
                AND loc.name = 'Video Games' THEN 'Explore Games'
            WHEN c.title LIKE '% ft %'
                AND loc.name = 'Video Games' THEN 'Featured'
            WHEN c.title LIKE '%wh 1%'
                AND loc.name = 'What''s Hot' THEN 'What''s Hot'
            ELSE ''
            END	AS 'Sub-Location'
        , c.StartDate AS 'Start Date'
        , c.EndDate AS 'End Date'
    FROM DMT.RetailTracker.Campaign c
        JOIN DMT.dbo.DateDimension dd ON dd.TimePeriod = c.StartDate
        JOIN DMT.RetailTracker.Promotion p ON p.CampaignId = c.CampaignId
        JOIN DMT.RetailTracker.Retailer r ON r.RetailerId = c.RetailerId
        JOIN DMT.dbo.PRD_Products prod ON prod.product_id = p.EntityId
        JOIN DMT.dbo.FAC_CampaignResults cr ON cr.CampaignId = c.CampaignId
            AND cr.check_value = 1
        JOIN DMT.dbo.FAC_Nodes loc ON loc.node_id = cr.node_id
            AND loc.parent_node_id = 213069
        JOIN DMT.dbo.FAC_RetailTrackerResults rr ON rr.promotion_id = p.PromotionId
            AND rr.node_id = 215198 AND rr.check_value = 1
        left JOIN DMT.dbo.FAC_RetailTrackerResults rr2
            ON rr2.promotion_id = p.PromotionId
            AND rr2.node_id = 215146
     WHERE r.RetailerId = ?
        AND (c.StartDate BETWEEN ? AND ?
            OR c.EndDate BETWEEN ? AND ?
            OR (c.StartDate <= ? AND (c.EndDate >= ? OR c.EndDate IS NULL)))
    ORDER BY [Location], [Sub-Location];
    '''
)
