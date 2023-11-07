const Radar = (eventsDiv) => {
  const {groupId, header, lang} = eventsDiv.dataset;
  const queryUrl = 'https://radar.squat.net/api/1.2/search/events.json?facets[group][]=' + groupId + '&fields=title,date_time,event_status,url&limit=10&language=' + lang;

  const getJSON = (url, callback) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = () => {
      const status = xhr.status;
      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
  };

  const formatEvents = (events) => {
    let eventHtml = '<h4>'+header+'</h4>';
    const dateFormat = { weekday: "short", month: "short", day: "2-digit" };
    const timeFormat = { hour: "2-digit", minute: "2-digit" };

    for (event of events) {
      eventHtml += '<p class="radar-event">';
      startDate = new Date(event.date_time[0].time_start);
      if (event.date_time[0].time_start != event.date_time[0].time_end) {
        endDate = new Date(event.date_time[0].time_end);
      } else {
        endDate = false;
      }

      startDateString = startDate.toLocaleDateString([lang], dateFormat);
      eventHtml += startDateString + ' ' + startDate.toLocaleTimeString([lang], timeFormat);
      if (endDate) {
        eventHtml += ' - ';
        endDateString = endDate.toLocaleDateString([lang], dateFormat);
        if (endDateString != startDateString) {
          eventHtml += endDateString + ' ';
        }
        eventHtml += endDate.toLocaleTimeString([lang], timeFormat);
      }
      eventHtml += ' <a href=" ' + event.url  + '" target="_blank">' + event.title + '</a>';
      eventHtml += '</p>';

    }
    return eventHtml;
  }

  getJSON(queryUrl,
    (err, data) => {
      if (err !== null) {
        console.log('Something went wrong: ' + err, data);
      } else {
        eventsArray = Object.values(data.result).filter((x) => x.event_status === "confirmed").sort((a, b) => a.date_time[0].value - b.date_time[0].value )
        if (eventsArray.length > 0) {
          eventsDiv.innerHTML = formatEvents(eventsArray);
        }
      }
    }
  );
};
