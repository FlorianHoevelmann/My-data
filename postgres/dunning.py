SELECT
user_created, now()-max(rev_timestamp) as time_neg
from lr_risk_model
inner join lr_account_aud using (user_created)
inner join dwh_adorable_transaction using(user_created)
where available_balance_cents/100 < -50
and end_timestamp >= now()
and type = 'DD'
and dwh_adorable_transaction.created > rev_timestamp - interval '2 Day'
and (lr_risk_model.id is null or max_overdraft_cents*(-1) > available_balance_cents)
group by user_created
