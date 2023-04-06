# Build stage
FROM ubuntu:22.04 AS build

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH=/opt/miniconda3/bin:$PATH

# Update and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        curl \
        unzip \
        apt-transport-https \
        ca-certificates \
        gnupg

# Install Google Chrome
RUN curl -sSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google-archive-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Install Chrome Driver
RUN CHROME_VERSION=$(dpkg -s google-chrome-stable | grep '^Version:' | awk '{print $2}' | cut -d '.' -f 1) && \
    CHROME_DRIVER_VERSION=$(curl -sL https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget -q https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -f chromedriver_linux64.zip

# Install Miniconda
WORKDIR /opt
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 && \
    rm -f Miniconda3-latest-Linux-x86_64.sh

# Update conda and install jupyterlab
RUN conda update conda && \
    conda install -y jupyterlab && \
    conda clean -afy

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip && \
    pip install pandas matplotlib seaborn matplotlib_venn \
        selenium webdriver_manager schedule && \
    rm -rf /root/.cache/pip

# Create JupyterLab settings directory and set theme
RUN mkdir -p /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/ && \
    echo '{ "theme": "JupyterLab Dark" }' > /root/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings

# Runtime stage
FROM ubuntu:22.04

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH=/opt/miniconda3/bin:$PATH

COPY --from=build /opt/miniconda3 /opt/miniconda3
COPY --from=build /root/.jupyter /root/.jupyter
COPY --from=build /opt/google/chrome /opt/google/chrome
COPY --from=build /usr/share/keyrings/google-archive-keyring.gpg /usr/share/keyrings/google-archive-keyring.gpg
COPY --from=build /etc/apt/sources.list.d/google-chrome.list /etc/apt/sources.list.d/google-chrome.list
COPY --from=build /usr/local/bin/chromedriver /usr/local/bin/chromedriver

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sudo \
        libglib2.0-0 \
        libnss3 \
        libx11-6 \
        libx11-xcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        libasound2 \
        libgbm1 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libatspi2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory and start JupyterLab
WORKDIR /
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--ServerApp.token="]

# $ docker build -t ubun_mini_jupy_chro_multi .
# $ docker run -p 8888:8888 -v "/mnt/c/Users/yourUserID/Desktop":/work --rm --name ubun_mini_jupy_chro_multi ubun_mini_jupy_chro_multi