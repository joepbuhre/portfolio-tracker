_vw_latestshareprices = """
create or replace view _vw_latestshareprices
as
select t.share_id,case when curr.currency = 'USD' then t.price / t.fxrate else price end as price
from (
	select sh.share_id, sh.close as price, sh.date, si.ticker, max(sh.date) over(partition by ticker), exchange.close as fxrate
	from share_history sh
	left join share_info si on si.id = sh.share_id
	left join (
		select * from share_history where share_id = (select id from share_info where ticker = 'EURUSD=X')
	) exchange on sh.date::date = exchange.date::date
) t
left join (
	select share_id, min(mutation_currency) as currency 
	from share_actions 
	where quantity is not null 
	group by share_id
) curr on curr.share_id = t.share_id
where t.max = t.date

"""