# The script pulls the local path to the database, and then, creates all the dimension and fact tables
# This script is too unique to apply to other datasets. However, it may be a good idea to create a template for connection and creation of data.
import sqlite3
import pandas as pd

# ── Connection ────────────────────────────────────────────────────────────────
# Update this path to match where your .db file lives locally
DB_PATH = r'C:\Users\jdsti\Documents\AdventureWorks-55MB-ETL\AdventureWorks.db'

conn = sqlite3.connect(DB_PATH)

# ── Fact Tables ───────────────────────────────────────────────────────────────

Sales_Internet = pd.read_sql_query("""
    SELECT
        f.SalesOrderNumber,
        f.SalesOrderLineNumber,
        f.OrderDate,
        f.DueDate,
        f.ShipDate,
        f.OrderQuantity,
        f.UnitPrice,
        f.ExtendedAmount,
        f.DiscountAmount,
        f.UnitPriceDiscountPct,
        f.ProductStandardCost,
        f.TotalProductCost,
        f.SalesAmount,
        f.TaxAmt,
        f.Freight,
        p.EnglishProductName          AS ProductName,
        p.ModelName,
        p.Color,
        p.Size,
        p.ProductLine,
        p.Class,
        p.Style,
        p.ListPrice,
        p.FinishedGoodsFlag,
        pc.EnglishProductCategoryName    AS ProductCategory,
        ps.EnglishProductSubcategoryName AS ProductSubcategory,
        c.CustomerAlternateKey,
        c.FirstName,
        c.LastName,
        c.Gender,
        c.YearlyIncome,
        c.TotalChildren,
        c.NumberChildrenAtHome,
        c.EnglishEducation            AS Education,
        c.EnglishOccupation           AS Occupation,
        c.HouseOwnerFlag,
        c.NumberCarsOwned,
        c.CommuteDistance,
        c.DateFirstPurchase,
        g.City,
        g.StateProvinceName           AS State,
        g.EnglishCountryRegionName    AS Country,
        g.PostalCode,
        t.SalesTerritoryRegion        AS TerritoryRegion,
        t.SalesTerritoryCountry       AS TerritoryCountry,
        t.SalesTerritoryGroup         AS TerritoryGroup,
        d.CalendarYear,
        d.CalendarQuarter,
        d.MonthNumberOfYear           AS MonthNumber,
        d.EnglishMonthName            AS MonthName,
        d.WeekNumberOfYear            AS WeekNumber,
        d.FiscalYear,
        d.FiscalQuarter,
        f.CurrencyKey,
        pr.EnglishPromotionName       AS PromotionName,
        pr.DiscountPct                AS PromotionDiscountPct,
        pr.EnglishPromotionType       AS PromotionType,
        pr.EnglishPromotionCategory   AS PromotionCategory
    FROM FactInternetSales f
    LEFT JOIN DimProduct p
        ON f.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory ps
        ON p.ProductSubcategoryKey = ps.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc
        ON ps.ProductCategoryKey = pc.ProductCategoryKey
    LEFT JOIN DimCustomer c
        ON f.CustomerKey = c.CustomerKey
    LEFT JOIN DimGeography g
        ON c.GeographyKey = g.GeographyKey
    LEFT JOIN DimSalesTerritory t
        ON f.SalesTerritoryKey = t.SalesTerritoryKey
    LEFT JOIN DimDate d
        ON f.OrderDateKey = d.DateKey
    LEFT JOIN DimPromotion pr
        ON f.PromotionKey = pr.PromotionKey
""", conn)

Sales_Reseller = pd.read_sql_query("""
    SELECT
        f.SalesOrderNumber,
        f.SalesOrderLineNumber,
        f.OrderDate,
        f.DueDate,
        f.ShipDate,
        f.OrderQuantity,
        f.UnitPrice,
        f.ExtendedAmount,
        f.DiscountAmount,
        f.UnitPriceDiscountPct,
        f.ProductStandardCost,
        f.TotalProductCost,
        f.SalesAmount,
        f.TaxAmt,
        f.Freight,
        p.EnglishProductName          AS ProductName,
        p.ModelName,
        p.Color,
        p.Size,
        p.ProductLine,
        p.Class,
        p.Style,
        p.ListPrice,
        p.FinishedGoodsFlag,
        pc.EnglishProductCategoryName    AS ProductCategory,
        ps.EnglishProductSubcategoryName AS ProductSubcategory,
        r.ResellerAlternateKey,
        r.ResellerName,
        r.BusinessType,
        r.NumberEmployees,
        r.AnnualSales,
        r.AnnualRevenue,
        r.YearOpened,
        r.ProductLine                 AS ResellerProductLine,
        r.OrderFrequency,
        r.FirstOrderYear,
        r.LastOrderYear,
        e.FirstName                   AS SalesRepFirstName,
        e.LastName                    AS SalesRepLastName,
        e.Title                       AS SalesRepTitle,
        e.DepartmentName              AS SalesRepDepartment,
        e.SalesPersonFlag,
        e.Status                      AS SalesRepStatus,
        g.City,
        g.StateProvinceName           AS State,
        g.EnglishCountryRegionName    AS Country,
        g.PostalCode,
        t.SalesTerritoryRegion        AS TerritoryRegion,
        t.SalesTerritoryCountry       AS TerritoryCountry,
        t.SalesTerritoryGroup         AS TerritoryGroup,
        d.CalendarYear,
        d.CalendarQuarter,
        d.MonthNumberOfYear           AS MonthNumber,
        d.EnglishMonthName            AS MonthName,
        d.WeekNumberOfYear            AS WeekNumber,
        d.FiscalYear,
        d.FiscalQuarter,
        f.CurrencyKey,
        pr.EnglishPromotionName       AS PromotionName,
        pr.DiscountPct                AS PromotionDiscountPct,
        pr.EnglishPromotionType       AS PromotionType,
        pr.EnglishPromotionCategory   AS PromotionCategory
    FROM FactResellerSales f
    LEFT JOIN DimProduct p
        ON f.ProductKey = p.ProductKey
    LEFT JOIN DimProductSubcategory ps
        ON p.ProductSubcategoryKey = ps.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc
        ON ps.ProductCategoryKey = pc.ProductCategoryKey
    LEFT JOIN DimReseller r
        ON f.ResellerKey = r.ResellerKey
    LEFT JOIN DimGeography g
        ON r.GeographyKey = g.GeographyKey
    LEFT JOIN DimEmployee e
        ON f.EmployeeKey = e.EmployeeKey
    LEFT JOIN DimSalesTerritory t
        ON f.SalesTerritoryKey = t.SalesTerritoryKey
    LEFT JOIN DimDate d
        ON f.OrderDateKey = d.DateKey
    LEFT JOIN DimPromotion pr
        ON f.PromotionKey = pr.PromotionKey
""", conn)

# ── Dimension Tables ──────────────────────────────────────────────────────────

Dim_Product = pd.read_sql_query("""
    SELECT
        p.ProductKey,
        p.ProductAlternateKey,
        p.EnglishProductName          AS ProductName,
        p.ModelName,
        p.Color,
        p.Size,
        p.SizeRange,
        p.ProductLine,
        p.Class,
        p.Style,
        p.StandardCost,
        p.ListPrice,
        p.DealerPrice,
        p.Weight,
        p.DaysToManufacture,
        p.FinishedGoodsFlag,
        p.Status,
        p.StartDate,
        p.EndDate,
        ps.EnglishProductSubcategoryName  AS ProductSubcategory,
        pc.EnglishProductCategoryName     AS ProductCategory
    FROM DimProduct p
    LEFT JOIN DimProductSubcategory ps
        ON p.ProductSubcategoryKey = ps.ProductSubcategoryKey
    LEFT JOIN DimProductCategory pc
        ON ps.ProductCategoryKey = pc.ProductCategoryKey
""", conn)

Dim_Customer = pd.read_sql_query("""
    SELECT
        c.CustomerKey,
        c.CustomerAlternateKey,
        c.FirstName,
        c.MiddleName,
        c.LastName,
        c.Gender,
        c.BirthDate,
        c.MaritalStatus,
        c.YearlyIncome,
        c.TotalChildren,
        c.NumberChildrenAtHome,
        c.EnglishEducation            AS Education,
        c.EnglishOccupation           AS Occupation,
        c.HouseOwnerFlag,
        c.NumberCarsOwned,
        c.CommuteDistance,
        c.DateFirstPurchase,
        c.EmailAddress,
        g.City,
        g.StateProvinceName           AS State,
        g.EnglishCountryRegionName    AS Country,
        g.PostalCode,
        g.SalesTerritoryKey
    FROM DimCustomer c
    LEFT JOIN DimGeography g
        ON c.GeographyKey = g.GeographyKey
""", conn)

Dim_Date = pd.read_sql_query("""
    SELECT
        DateKey,
        FullDateAlternateKey          AS FullDate,
        EnglishDayNameOfWeek          AS DayName,
        DayNumberOfWeek,
        DayNumberOfMonth,
        DayNumberOfYear,
        WeekNumberOfYear              AS WeekNumber,
        EnglishMonthName              AS MonthName,
        MonthNumberOfYear             AS MonthNumber,
        CalendarQuarter,
        CalendarYear,
        CalendarSemester,
        FiscalQuarter,
        FiscalYear,
        FiscalSemester
    FROM DimDate
""", conn)

Dim_Territory = pd.read_sql_query("""
    SELECT
        SalesTerritoryKey,
        SalesTerritoryAlternateKey,
        SalesTerritoryRegion          AS TerritoryRegion,
        SalesTerritoryCountry         AS TerritoryCountry,
        SalesTerritoryGroup           AS TerritoryGroup
    FROM DimSalesTerritory
""", conn)

Dim_Promotion = pd.read_sql_query("""
    SELECT
        PromotionKey,
        EnglishPromotionName          AS PromotionName,
        DiscountPct,
        EnglishPromotionType          AS PromotionType,
        EnglishPromotionCategory      AS PromotionCategory,
        StartDate,
        EndDate,
        MinQty,
        MaxQty
    FROM DimPromotion
""", conn)

Dim_Currency = pd.read_sql_query("""
    SELECT
        CurrencyKey,
        CurrencyAlternateKey          AS CurrencyCode,
        CurrencyName
    FROM DimCurrency
""", conn)

Dim_SalesReason = pd.read_sql_query("""
    SELECT
        SalesReasonKey,
        SalesReasonAlternateKey,
        SalesReasonName,
        SalesReasonReasonType         AS SalesReasonType
    FROM DimSalesReason
""", conn)

# ── Bridge Table ─────────────────────────────────────────────────────────────

Bridge_SalesReason = pd.read_sql_query("""
    SELECT
        SalesOrderNumber,
        SalesOrderLineNumber,
        SalesReasonKey
    FROM FactInternetSalesReason
""", conn)

# ── Close connection ──────────────────────────────────────────────────────────
conn.close()
