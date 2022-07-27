document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#formUpload');
    const field = document.querySelector('#fileUpload');

    field.addEventListener('change', event => {
        console.log('ok');

        let files = event.target.files;
        let fileName = files[0].name;

        let fNames = [];

        console.log(fNames);
        console.log(fileName);

        for (let i = 0; i < files.length; i++) {
            fNames.push(files[i].name.slice(0, -3) + 'xls');
        }

        console.log('fil:', files);

        const formData = new FormData(form);

        formData.append('files', files[0]);
        formData.append('name', fileName);
        console.log(formData.get('files'));


        //let url = 'http://localhost:5000/sendData';
        let url = 'http://localhost:5000/sendData';
        fetch(url, {
            method: "POST",
            body: formData
        })
            .then(response => response.json())
            .then(res => {
                console.log('success');
                console.log(res);
            }).finally(() => {
                form.reset();

                //const time = 10000;
                //console.log(time);

                fNames.forEach(item => {
                    let url = `http://localhost:5000/download/${item}`;
                    console.log('url', url);
                    fetch(url)
                        .then(res => res.blob())
                        .then(blob => {
                            download(blob);
                        });
                });

                // setTimeout(() => {
                //     fNames.forEach(item => {
                //         let url = `http://localhost:5000/download/${item}`;
                //         console.log(url);
                //         fetch(url)
                //             .then(res => {
                //                 return res.blob();
                //             })
                //             .then(blob => {
                //                 download(blob);
                //             });
                //     });
                // }, time);


            });
    });

}); 