# 2018 Spring AC297r MBTA Rider Segmentation

This is the repository that hosts the codes for the full app. For more details, please visit our Github [organization](https://github.com/AC297r-MBTA-2018/).


## Project Overview

The Massachusetts Bay Transportation Authority (MBTA) is the largest public transportation agency in New England, delivering a complex system of subway, bus, commuter rail, light rail, and ferry services to riders in the dynamic economy of the Greater Boston Area. It is estimated that MBTA provides over 1.3 million trips on an average weekday. While MBTA collects a wealth of trip transaction data on a daily basis, a persistent limitation has been the organization’s lack of knowledge around rider groups and their respective ridership habits. Understanding rider segmentation in the context of pattern-of-use has significant implications in developing new policies to improve its service planning and potentially changing its fare structure. Therefore, we aim to develop a flexible, reusable rider segmentation model on MBTA’s “core system” (encompassing local buses and subway) that can group individuals according to pattern-of-use dimensions.


## Navigating our Github Organization

- **Rider-Segmentation-Full-App**: [This](https://github.com/AC297r-MBTA-2018/Rider-Segmentation-Full-App) is the code base for both the Python segmentation package and the app with full functionality (i.e. based on user input, the app is able to send clustering request to the Flask backend on a new data set or user-specified weights/duration that has not been cached. Disclaimer: The full input source is not available on Github for security reasons, and each new clustering request takes at least several hours.)
- **Dashboard**: [This](https://github.com/AC297r-MBTA-2018/Dashboard) is the static version of the full app that has limited functionality (The app is only able to display pre-ran monthly clustering results for Dec 2016 to Nov 2017 with equal weighting on temporal, geographical and ticket purchasing pattern.) The app is deployed as a Github page (https://ac297r-mbta-2018.github.io/Dashboard/).
- **Final-Report**: [This](https://github.com/AC297r-MBTA-2018/Final-Report) repository hosts the final report which is deployed as a Github page (https://ac297r-mbta-2018.github.io/Final-Report/).
- **Code-Documentation**: [This](https://github.com/AC297r-MBTA-2018/Code-Documentation) repository hosts the content of this code documentation which is deployed as a Github page, *current page*.

Note: The limited Dashboard, Final Report and Code Documentation are linked via a navigation bar on respective Github pages.
