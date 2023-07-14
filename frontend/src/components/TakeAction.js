import React from 'react';
import { Accordion } from "react-bootstrap";


export default function TakeAction () {
    React.useEffect(() => {
        document.title = "Take Action";
    }, []);
    return (
 <div class="main" id="action-page">
    <p>
        The information below has been aggregated from the City of Albany’s <a target="_blank" href="https://www.albanyny.gov/1944/Tenant-Resources-Information">Albany Tenant Resource & Information Center</a> and the United Tenants of
        Albany’s (UTA) <a target="_blank" href="https://utalbany.org/for-tenants/">resources for tenants</a>. Please visit these sites for the most up to date resources and information.
    </p>

    <div class="row">
        <div class="col-8">
            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>My rights as a tenant have been violated.</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                            <p><a href="https://utalbany.org/know-your-rights/">Know your rights as a renter.</a></p>
                            <p>For assistance or guidance in pursuing civil legal action against a landlord, visit <a href="https://nycourts.gov/courthelp/">New York State CourtHelp</a> for a variety of self-help resources.</p>
                            <p>You may also try contacting the <strong>Legal Aid Society of Northeastern New York</strong> at (833) 628-0087.</p>
                            <p>For tenant advocacy or mediation services, contact <strong>United Tenants of Albany </strong>at (518) 436-8997 x3.</p>
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>I'm facing eviction.</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                            <p>For tenants facing eviction, the <strong>worst thing to do is to do nothing</strong>.&nbsp;</p>
                            <p>Pay attention to any court dates or deadlines. Talk to your landlord - can you work out a payment plan? Apply for assistance? Fix the lease violations?</p>
                            <p>Contact the <strong>Legal Aid Society of Northeastern New York</strong> at <strong>(833) 628-0087</strong> to see if you may be eligible for free civil legal services.&nbsp;</p>
                            Tenants in New York State who have been impacted financially by COVID-19 are protected from eviction until January 15, 2022. You must fill out a copy of the
                            <a href="https://nycourts.gov/eefpa/PDF/Residential_Eviction_Hardship_Declaration-English.pdf">Tenant's Declaration of Hardship During the COVID-19 Pandemic</a> in order to be protected.
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>I'm behind on rent or utilities.</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                                <p>
                                    <strong>United Tenants of Albany</strong> is currently the community's primary rental assistance provider. They also have some funding for utility assistance. UTA can be reached by phone at
                                    <strong>(518) 436-8997 x3</strong>. More information on financial assistance from UTA can be found <a href="https://utalbany.org/for-tenants/#:~:text=UTA%20Financial%20Assistance%20Service">here</a>.
                                </p>
                                The <strong>Home Energy Assistance Program </strong>from the Albany County Department of Social Services is also open and accepting applications for utility assistance. To learn more or apply, call
                                <strong>(518) 447-7323</strong>.
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>I am interested in learning about how to form a Tenant Association in my building.</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                         <strong>United Tenants of Albany</strong> is able to support tenants in the City of Albany who want to canvas their neighbors, hold tenant meetings, and form a Tenant Association. Tenant Associations are a
                                powerful way to bargain with your landlord for repairs and have tenant voices be heard. Call <strong>(518) 436-8997 x3 </strong>to be connected to a tenant organizer.
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>I have code violations in my apartment.</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                                <p>First,&nbsp; alert your landlord to anything broken or dangerous in your apartment. Make sure this is in writing. (text, e-email, certified mail)</p>

                                If your landlord does not fix the issue, reach out to code enforcement at&nbsp;<strong>518-434-5995 or by emailing </strong><a href="mailto:codes@albanyny.gov"><strong>codes@albanyny.gov</strong></a>. Code
                                enforcement will ask for your contact information and set up a date/time to come inspect the property.

                                <p>Code enforcement is likely not going to solve all of your habitability issues, but is a tool for tenants to use to improve their housing.</p>
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>I need help finding an apartment.</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                                    <p>Finding &amp; Applying for Housing: This <em>Good Neighbor School </em>module covers tips for&nbsp; searching for housing and getting through the rental application process.&nbsp;&nbsp;</p>
                                    <p>Capital Region Affordable Housing Directory: This guidebook includes many&nbsp; affordable housing developments in the region. <em>Note: Some may be on waitlists.&nbsp;</em></p>
                                    Affordable Rental Listing (ARL): This is a resource prepared by Fawn Dalton at the&nbsp; Albany Housing Coalition. To join the monthly distribution list, you can contact&nbsp; Fawn by emailing
                                    f.dalton@ahcvets.org.
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>

            <Accordion>
              <Accordion.Item eventKey="0">
                <Accordion.Header><h5>I want to check to see if my building/apartment has a Residential Occupancy Permit (ROP).</h5></Accordion.Header>
                <Accordion.Body>
                <span class="action-accordion-body">
                            <p>To check if your building has an current ROP <a target="_blank" href="https://www.albanyny.gov/DocumentCenter/View/2369/Active-Residential-Occupancy-Permits-12152021?bidId=">check this list.</a></p>
                            <strong>If you do not see your property listed here, reach out to code enforcement at 518-434-5995 or by emailing <a href="mailto:codes@albanyny.gov">codes@albanyny.gov</a> to clarify why.</strong>
                </span>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
            </div>
        </div>
    </div>

    );
}
