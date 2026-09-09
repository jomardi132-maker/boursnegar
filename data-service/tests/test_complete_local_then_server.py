from scripts.complete_local_then_server import classify

def test_classification_separates_company_fund_and_derived():
    remote=[{'symbol':'فملی','status':'incomplete','industry':'فلزات اساسی'},
            {'symbol':'دارا یکم','status':'incomplete','industry':'صندوق سرمایه گذاری قابل معامله'},
            {'symbol':'فملیح','status':'incomplete','industry':'فلزات اساسی'},
            {'symbol':'کامل','status':'complete','industry':'فلزات اساسی'}]
    local={row['symbol']:{'status':row['status']} for row in remote}
    result=classify(remote,local)
    assert result['recoverable_companies']==['فملی']
    assert result['funds_separate_model']==['دارا یکم']
    assert result['derived_not_applicable']==['فملیح']
    assert result['already_sufficient']==['کامل']
