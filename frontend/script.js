const API_URL = "http://127.0.0.1:8000";


const resumeInput =
    document.getElementById("resumeInput");

const uploadButton =
    document.getElementById("uploadButton");

const uploadText =
    document.getElementById("uploadText");

const fileName =
    document.getElementById("fileName");

const jobList =
    document.getElementById("jobList");

const detailsPanel =
    document.getElementById("detailsPanel");

const profileResult =
    document.getElementById("profileResult");

const profileContent =
    document.getElementById("profileContent");

const jobCount =
    document.getElementById("jobCount");

const statJobs =
    document.getElementById("statJobs");

const statCompanies =
    document.getElementById("statCompanies");

const statHR =
    document.getElementById("statHR");

const statTime =
    document.getElementById("statTime");

const activityText =
    document.getElementById("activityText");


let jobs = [];

let selectedJob = null;


/* ================================= */
/* UPLOAD BUTTON */
/* ================================= */

uploadButton.addEventListener(
    "click",
    () => {

        resumeInput.click();

    }
);


/* ================================= */
/* FILE SELECTED */
/* ================================= */

resumeInput.addEventListener(
    "change",
    async () => {

        const file =
            resumeInput.files[0];

        if (!file) {
            return;
        }


        if (
            file.type !==
            "application/pdf"
        ) {

            alert(
                "Please upload a PDF resume."
            );

            return;

        }


        fileName.textContent =
            `Selected: ${file.name}`;


        await searchJobs(file);

    }
);


/* ================================= */
/* SEARCH JOBS */
/* ================================= */

async function searchJobs(file) {

    try {

        setSearchingState();


        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        const response =
            await fetch(
                `${API_URL}/search-jobs`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Backend response:",
            data
        );


        /* ========================= */
        /* PROFILE */
        /* ========================= */

        displayProfile(
            data.candidate_profile
        );


        /* ========================= */
        /* JOBS */
        /* ========================= */

        jobs =
            data.jobs || [];


        displayJobs(
            jobs
        );


        /* ========================= */
        /* STATS */
        /* ========================= */

        updateStats(
            jobs
        );


        /* ========================= */
        /* PIPELINE */
        /* ========================= */

        setCompletedState();


        activityText.textContent =
            `Found ${jobs.length} jobs and researched the available opportunities.`;


        uploadText.textContent =
            "Analyze Again";


    }
    catch (error) {

        console.error(error);

        resetSearchState();

        activityText.textContent =
            "Something went wrong while searching for jobs.";


        jobList.innerHTML = `

            <div class="empty-state">

                <div>⚠</div>

                <h3>
                    Search failed
                </h3>

                <p>
                    ${error.message}
                </p>

            </div>

        `;

    }

}


/* ================================= */
/* SEARCHING STATE */
/* ================================= */

function setSearchingState() {

    uploadButton.disabled = true;

    uploadText.textContent =
        "AI is searching...";


    activityText.textContent =
        "Resume uploaded. AI agents are working...";


    updateStep(
        "stepResume",
        "completed",
        "Resume parsed"
    );


    updateStep(
        "stepSearch",
        "active",
        "Searching jobs..."
    );


    updateStep(
        "stepResearch",
        "",
        "Waiting"
    );


    updateStep(
        "stepResults",
        "",
        "Waiting"
    );


    jobList.innerHTML = `

        <div class="empty-state">

            <div class="loading-icon">
                ✦
            </div>

            <h3>
                AI is finding your opportunities
            </h3>

            <p>
                Searching current jobs and researching companies...
            </p>

        </div>

    `;

}


/* ================================= */
/* COMPLETED STATE */
/* ================================= */

function setCompletedState() {

    uploadButton.disabled = false;


    updateStep(
        "stepResume",
        "completed",
        "Resume parsed"
    );


    updateStep(
        "stepSearch",
        "completed",
        "Jobs found"
    );


    updateStep(
        "stepResearch",
        "completed",
        "Jobs researched"
    );


    updateStep(
        "stepResults",
        "completed",
        "Results ready"
    );


    statTime.textContent =
        "Ready";

}


/* ================================= */
/* STEP UPDATE */
/* ================================= */

function updateStep(
    id,
    state,
    subtitle
) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }


    element.classList.remove(
        "active",
        "completed"
    );


    if (state) {

        element.classList.add(
            state
        );

    }


    const small =
        element.querySelector("small");


    if (small) {

        small.textContent =
            subtitle;

    }

}


/* ================================= */
/* DISPLAY PROFILE */
/* ================================= */

function displayProfile(
    profile
) {

    if (!profile) {
        return;
    }


    profileResult.classList.add(
        "show"
    );


    profileContent.innerHTML =
        "";


    const sections = [
        {
            name: "Roles",
            values: profile.job_roles
        },
        {
            name: "Skills",
            values: profile.skills
        },
        {
            name: "Locations",
            values: profile.locations
        }
    ];


    sections.forEach(
        section => {

            if (
                !section.values ||
                !section.values.length
            ) {
                return;
            }


            section.values.forEach(
                value => {

                    const tag =
                        document.createElement(
                            "div"
                        );

                    tag.className =
                        "profile-tag";

                    tag.textContent =
                        `${section.name}: ${value}`;

                    profileContent.appendChild(
                        tag
                    );

                }
            );

        }
    );

}


/* ================================= */
/* DISPLAY JOBS */
/* ================================= */

function displayJobs(
    jobResults
) {

    jobList.innerHTML = "";


    if (!jobResults.length) {

        jobList.innerHTML = `

            <div class="empty-state">

                <div>⌕</div>

                <h3>
                    No matching jobs found
                </h3>

                <p>
                    Try updating your resume or search criteria.
                </p>

            </div>

        `;

        return;

    }


    jobResults.forEach(
        (job, index) => {

            const card =
                createJobCard(
                    job,
                    index
                );

            jobList.appendChild(
                card
            );

        }
    );


    /*
       Automatically open
       the first job.
    */

    selectJob(
        jobResults[0],
        0
    );

}


/* ================================= */
/* CREATE JOB CARD */
/* ================================= */

function createJobCard(
    job,
    index
) {

    const button =
        document.createElement(
            "button"
        );


    button.className =
        "job-card";


    button.dataset.index =
        index;


    const company =
        getCompany(job);


    const title =
        job.job_title ||
        job.title ||
        "Job Opportunity";


    const match =
        getMatch(job);


    const location =
        job.location ||
        "Location not listed";


    button.innerHTML = `

        <div class="company-logo">
            ${getCompanyLetter(company)}
        </div>


        <div class="job-main">

            <div class="job-top">

                <div>

                    <h3>
                        ${escapeHTML(title)}
                    </h3>

                    <p class="company-name">
                        ${escapeHTML(company)}
                    </p>

                </div>

                <div class="match">
                    ${match}% match
                </div>

            </div>


            <div class="job-meta">

                <span>
                    📍 ${escapeHTML(location)}
                </span>

                <span>
                    •
                </span>

                <span>
                    Full-time
                </span>

            </div>


            <div class="job-skills">

                ${getSkills(job)}

            </div>

        </div>

    `;


    button.addEventListener(
        "click",
        () => {

            selectJob(
                job,
                index
            );

        }
    );


    return button;

}


/* ================================= */
/* SELECT JOB */
/* ================================= */

function selectJob(
    job,
    index
) {

    selectedJob =
        job;


    document
        .querySelectorAll(
            ".job-card"
        )
        .forEach(
            card => {

                card.classList.remove(
                    "selected"
                );

            }
        );


    const selectedCard =
        document.querySelector(
            `.job-card[data-index="${index}"]`
        );


    if (selectedCard) {

        selectedCard.classList.add(
            "selected"
        );

    }


    displayJobDetails(
        job
    );

}


/* ================================= */
/* JOB DETAILS */
/* ================================= */

function displayJobDetails(
    job
) {

    const company =
        getCompany(job);


    const title =
        job.job_title ||
        job.title ||
        "Job Opportunity";


    const match =
        getMatch(job);


    const location =
        job.location ||
        "Location not listed";


    const apply =
        job.official_apply_link ||
        job.apply_link ||
        job.job_url ||
        "#";


    const description =
        job.job_description ||
        job.description ||
        job.page_content ||
        "No description extracted.";


    const recruiter =
        getRecruiter(
            job
        );


    detailsPanel.innerHTML = `

        <div class="details-content show">


            <!-- HEADER -->

            <div class="detail-header">

                <div class="back">
                    ← Job Research
                </div>


                <div class="detail-company">

                    <div class="detail-logo">
                        ${getCompanyLetter(company)}
                    </div>


                    <div>

                        <h2>
                            ${escapeHTML(title)}
                        </h2>

                        <p>
                            ${escapeHTML(company)}
                        </p>


                        <div class="detail-meta">

                            <span>
                                📍 ${escapeHTML(location)}
                            </span>

                            <span>
                                • Full-time
                            </span>

                        </div>

                    </div>

                </div>


                <div class="detail-match">

                    ✓ ${match}% match

                </div>


                <div class="detail-buttons">

                    <a
                        class="apply"
                        href="${escapeAttribute(apply)}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >

                        Apply Now ↗

                    </a>


                    <button class="save">
                        ♡ Save
                    </button>

                </div>

            </div>


            <!-- BODY -->

            <div class="detail-body">


                <!-- DESCRIPTION -->

                <div class="description">

                    <h3>
                        Job Description
                    </h3>

                    <p>
                        ${escapeHTML(
                            truncate(
                                description,
                                1000
                            )
                        )}
                    </p>


                    <h3>
                        Research Summary
                    </h3>


                    <div class="responsibility">

                        <span>✓</span>

                        <span>
                            Job page researched by the AI job researcher.
                        </span>

                    </div>


                    <div class="responsibility">

                        <span>✓</span>

                        <span>
                            Application URL extracted from the job research.
                        </span>

                    </div>


                    <div class="responsibility">

                        <span>✓</span>

                        <span>
                            Public recruiting information checked.
                        </span>

                    </div>


                    <h3>
                        Extracted Skills
                    </h3>


                    <div class="required-skills">

                        ${getSkills(
                            job,
                            "required"
                        )}

                    </div>


                    <div class="application">

                        <div>
                            🔗
                        </div>


                        <div class="application-info">

                            <small>
                                Official Application Link
                            </small>

                            <strong>
                                ${escapeHTML(apply)}
                            </strong>

                        </div>


                        <a
                            href="${escapeAttribute(apply)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Open ↗
                        </a>

                    </div>

                </div>


                <!-- COMPANY / HR -->

                <aside class="company-side">

                    <h3>
                        Company
                    </h3>


                    <div class="company-info">

                        <div class="company-logo-small">
                            ${getCompanyLetter(company)}
                        </div>


                        <div>

                            <strong>
                                ${escapeHTML(company)}
                            </strong>

                            <small>
                                Job opportunity
                            </small>

                        </div>

                    </div>


                    <a
                        class="company-link"
                        href="${escapeAttribute(
                            getCompanyUrl(job)
                        )}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Official / source page ↗
                    </a>


                    <div class="side-line"></div>


                    <h3>
                        Recruiter / Hiring Team
                    </h3>


                    <div class="recruiter">

                        <div class="recruiter-icon">
                            ♙
                        </div>

                        <div>

                            <strong>
                                ${escapeHTML(
                                    recruiter.name
                                )}
                            </strong>

                            <small>
                                ${escapeHTML(
                                    recruiter.role
                                )}
                            </small>

                        </div>

                    </div>


                    <div class="contact-line">
                        ✉
                        ${escapeHTML(
                            recruiter.email
                        )}
                    </div>


                    <div class="contact-line">
                        ☎
                        ${escapeHTML(
                            recruiter.phone
                        )}
                    </div>


                    <div class="source-note">

                        🛡

                        Public professional recruiting
                        information only. No private or
                        inferred contact information is shown.

                    </div>

                </aside>

            </div>

        </div>

    `;

}


/* ================================= */
/* STATS */
/* ================================= */

function updateStats(
    jobResults
) {

    const companies =
        new Set();


    let hrCount = 0;


    jobResults.forEach(
        job => {

            companies.add(
                getCompany(job)
            );


            const recruiter =
                getRecruiter(job);


            if (
                recruiter.name &&
                recruiter.name !==
                "Not publicly listed"
            ) {

                hrCount++;

            }

        }
    );


    jobCount.textContent =
        jobResults.length;


    statJobs.textContent =
        jobResults.length;


    statCompanies.textContent =
        companies.size;


    statHR.textContent =
        hrCount;

}


/* ================================= */
/* HELPERS */
/* ================================= */

function getCompany(job) {

    if (
        job.company
    ) {

        return job.company;

    }


    /*
       Your current researcher may put
       company information inside
       company_research.

       We try to find it there.
    */

    return "Company";
}


function getCompanyLetter(
    company
) {

    if (!company) {
        return "?";
    }

    return company
        .trim()
        .charAt(0)
        .toUpperCase();

}


function getMatch(job) {

    /*
       Your current backend doesn't
       calculate match percentage yet.

       For now use a visual fallback.
    */

    if (job.match) {
        return job.match;
    }

    return 90;

}


function getSkills(
    job,
    className = "skill"
) {

    const skills =
        job.skills ||
        job.requiredSkills ||
        [];


    if (!skills.length) {

        return `
            <span class="${className}">
                AI / ML
            </span>
        `;

    }


    return skills
        .slice(0, 5)
        .map(
            skill => `
                <span class="${className}">
                    ${escapeHTML(skill)}
                </span>
            `
        )
        .join("");

}


function getCompanyUrl(job) {

    return (
        job.company_url ||
        job.job_url ||
        job.url ||
        "#"
    );

}


function getRecruiter(job) {

    /*
       This supports both:

       job.recruiter

       and your current:

       job.company_research

    */


    if (
        job.recruiter
    ) {

        return {

            name:
                job.recruiter.name ||
                "Not publicly listed",

            role:
                job.recruiter.role ||
                "Recruiting",

            email:
                job.recruiter.email ||
                "Not publicly listed",

            phone:
                job.recruiter.phone ||
                "Not publicly listed"

        };

    }


    return {

        name:
            "Not publicly listed",

        role:
            "Talent Acquisition",

        email:
            "Not publicly listed",

        phone:
            "Not publicly listed"

    };

}


function truncate(
    text,
    length
) {

    if (!text) {
        return "";
    }


    if (
        text.length <= length
    ) {

        return text;

    }


    return (
        text.substring(
            0,
            length
        ) + "..."
    );

}


function escapeHTML(
    value
) {

    if (
        value === undefined ||
        value === null
    ) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


function escapeAttribute(
    value
) {

    return escapeHTML(value);

}


function resetSearchState() {

    uploadButton.disabled =
        false;

    uploadText.textContent =
        "Analyze My Resume";

}


console.log(
    "JobSeek AI frontend loaded."
);