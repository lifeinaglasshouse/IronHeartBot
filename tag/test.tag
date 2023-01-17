(do 
    (decl u, r)
    (set u = arg.get(0) or user)
    (set r = rand(1, 12))
    (if (r > 50)
        (return "{} is based ({}%)".f(u.name, r))
        (return "{} is cringe ({}%)".f(u.name, r))
    )
)