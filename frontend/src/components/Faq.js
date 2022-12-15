import React from 'react';


export default function Faq () {
    React.useEffect(() => {
        document.title = "FAQ";
    }, []);
    return (
    <div class="main">
        <h2>Frequently Asked Questions</h2>
        <br />
        <p><strong>What is the use of this site?</strong></p>
        <p>This site allows both prospective and current renters to look up a landlord and learn some additional facts about that person or entity. Presently, there is little transparency in the renting process and no democratic infrastructure to support such. This is a compilation of public information and relevant private information utilized to assist tenants in deciding a variety of questions relevant to every tenant. Is this property important to the landlord or just one of many hoarded homes? Does the landlord have a history of code violations? How often are the police being called to the home for landlord-tenant issues? How does one landlord’s statistics compare to the city average? Most importantly, is this somewhere you want to live?</p>

        <p><strong>How do I use this site?</strong></p>
        <p>Simply type your landlord’s name or the property address in the search box to get a general landlord report and grade. The address listed under your landlord’s name is their address, which is where you would sue them in small claims court. If a P.O. # is listed, you will need to dig a little deeper, because you cannot sue a P.O. box. You may choose to call the City of Albany’s Tax Assessor directly, pull an eviction petition from the Albany City Court Clerk filed by your landlord, or review mortgages at <a href="https://www.searchiqs.com/nyalb">https://www.searchiqs.com/nyalb</a>. If there are Associated Landlords listed, these are entities or people linked to your landlord, being separate LLCs, family, differently spelled names, etc. The landlord size is broken into four categories: Small (1 property owned), Medium (between 1 and 4 properties owned), Large (Between 5 and 10 properties owned), and Very Large (more than 10 properties owned). Generally, the more properties a landlord has the more tenant complaints, code violations and landlord-tenant police incidents they will have. However, we also know that some landlords treat different tenants differently. For example, a tenant in Pine Hills may have a good relationship with the same landlord a tenant in West Hill has a bad relationship with. In order to adjust for home-hoarders, we have a list of properties owned by a given entity, and properties associated with a given entity, that are hyperlinked. By clicking the hyperlink, you can presumably determine the condition of the housing you are searching for. The listed complaints, violations and incidents are recorded since the landlord took the property over, rather than a historical record. Below the listed links is a map representative of the properties owned by the landlord.</p>

        <p><strong>How are the scores decided?</strong></p>
        <p>The overall landlord score is aggregated based on the amount of registered tenant complaints, code violations, and landlord-tenant police incidents at the address. Tenant complaints are so far based on the amount of complaints registered by a multitude of agencies across the City of Albany. You can use this link <a href="https://forms.gle/1fWCfhKFwBiJDjoM9">https://forms.gle/1fWCfhKFwBiJDjoM9</a> to register a complaint, and we will manually add it to the overall score as frequently as possible. Code violations are pulled directly from the City of Albany, via the Building Blocks website. All calls related to registering Residential Occupancy Permits have been removed so as not to inaccurately damage the landlord’s violations report. Landlord-Tenant police incidents are recorded by the Albany Police Department. We know that the likelihood of eviction correlates with the amount of landlord-tenant police incidents. Added in the category boxes are the total complaints, violations or incidents, and average of indicators per category, and the City of Albany average of each category. Our hope is that these categories allow tenants to make informed decisions about dealing with their landlord.</p>

        <p><strong>What is an LLC?</strong></p>
        <p>A Limited Liability Company (LLC) is a business structure which protects its owners from being personally responsible for liability and debts. This means rather than suing an individual landlord for their belongings you are suing an entity. LLCs are also a means of obfuscating who actually owns a property, making it increasingly difficult to determine who you are paying and who is responsible for your household wellbeing. What’s more, it can be very difficult to sue an LLC. To establish an LLC, members must have a lawyer on retainer.</p>

        <p><strong>Where does the information come from?</strong></p> 
        <p>All data utilized is public information from the City of Albany.</p>
    </div>
    );
}
