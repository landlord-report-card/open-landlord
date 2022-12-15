import React from 'react';


export default function About () {
    React.useEffect(() => {
        document.title = "About";
    }, []);
    return (
        <div className="main">

            <p><strong>About the Landlord Report Card</strong></p>
            <p>The Landlord Report Card is a volunteer-led, grassroots project based in Albany, NY, working to provide greater transparency into the City's data for tenants across the city. It is an open-source project whose code is available here: <a target="_blank" rel="noreferrer" href="https://github.com/landlord-report-card/open-landlord">https://github.com/landlord-report-card/open-landlord</a></p>

            <p><strong>Contact Us</strong></p>
            <p>If you have feedback on the site or wish to get into contact with the developers and maintainers of the site, you can email us at <a href="mailto:info@albanylandlord.com">info@albanylandlord.com</a></p>

        </div>
    );
}
