import React from 'react';


export default function About () {
    React.useEffect(() => {
        document.title = "About";
    }, []);
    return (
        <div className="main">

            <p><strong>About the Landlord Report Card</strong></p>
            <p>The Landlord Report Card is a volunteer-led, grassroots project based in Albany, NY, working to provide greater transparency into the City's data for tenants across the city. It is an open-source project whose code is available here: <a target="_blank" rel="noreferrer" href="https://github.com/landlord-report-card/open-landlord">https://github.com/landlord-report-card/open-landlord</a></p>

            <p><strong>About the Data</strong></p>
            <p>All data is provided by the City of Albany, and any errors, omissions, and inaccuracies should be reported to the City of Albany. This data is provided for informational purposes, as a public resource for general information. You should not rely on this information for any business, legal, or other decision. The Albany Landlord Report Card is not responsible for and disclaims responsibility for any losses or damages, directly or otherwise, which may result from the use of this data.</p>

            <p><strong>Grading</strong></p>
            <p>All grade assignments use academic grading based on standard deviation from the mean. The top grade, A, is given for performance that exceeds the mean by more than 1.5 standard deviations, a B for performance between 0.5 and 1.5 standard deviations above the mean, and so on. More info is available <a href="https://en.wikipedia.org/wiki/Academic_grading_in_the_United_States#Rank-based_grading
">here.</a></p>

            <p><strong>Contact Us</strong></p>
            <p>If you have feedback on the site or wish to get into contact with the developers and maintainers of the site, you can email us at <a href="mailto:info@albanylandlord.com">info@albanylandlord.com</a></p>



        </div>
    );
}
