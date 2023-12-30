var ckInstances = {};
window.ckInstances = ckInstances;

initializeEditor('.editor', 'word-count-body', 'character-count-body', 'post', postID);
repliesData.forEach(function(reply) {
    initializeEditor('.editor-' + reply.pk, 'word-count-body-' + reply.pk, 'character-count-body-' + reply.pk, 'reply', reply.pk);
});

function initializeEditor(id, wordCount, characterCount, type, entityId, data) {
	var watchdog = new CKSource.EditorWatchdog();
	var uniqueId = type + '-' + entityId;
	ckInstances[uniqueId] = watchdog;
	
	watchdog.setCreator( ( element, config ) => {
	
		return CKSource.Editor
			
			.create( element, config )
			.then( editor => {
				return editor;
			} );
	} );
	
	watchdog.setDestructor( editor => {
		return editor.destroy();
	} );
	
	watchdog.on( 'error', handleSampleError );

	watchdog
	.create( document.querySelector( id ), {
		isReadOnly: true,
		wordCount: {
            onUpdate: stats => {
				document.getElementById(wordCount).textContent = stats.words;
				document.getElementById(characterCount).textContent = stats.characters;
            }
        },
		toolbar: {
			items: [
				"heading",
				"|", 
				"bold", "underline", "italic", "strikethrough",
				"|", 
				"fontBackgroundColor", "fontColor", "fontFamily", "fontSize", 
				"|", 
				"outdent", "indent", "alignment", 
				"|", 
				"timeStamp",
				"-", 
				"link","bulletedList", "numberedList", 
				"|", 
				"highlight", "code", "removeFormat", 
				"|", 
				"imageInsert", "mediaEmbed", 
				"|", 
				"blockQuote", "insertTable", "specialCharacters", 
				"|", 
				"findAndReplace", "selectAll", 
				"|", 
				"redo", "undo"],
			shouldNotGroupWhenFull: true
		},
		language: "en",
		image: {
			toolbar: ["imageTextAlternative", "toggleImageCaption", "imageStyle:inline", "imageStyle:block", "imageStyle:side", "linkImage"]
		},
		table: {
			contentToolbar: ["tableColumn", "tableRow", "mergeTableCells", "tableCellProperties", "tableProperties"]
		},
	} )
	.then( editor => {
		editor = watchdog.editor;
		
		ckInstances[uniqueId].editor = editor;

		const toolbarElement = editor.ui.view.toolbar.element;
		const editableElement = editor.editing.view.getDomRoot();
		const editorContainer = editableElement.parentElement;

		editor.enableReadOnlyMode('{{ post.id }}');
		editor.isReadOnly; 

		toolbarElement.style.display = 'none';

		if(data){
			editor.setData(data);
		}
	})
	.catch( handleSampleError );
}

function handleSampleError( error ) {
	const issueUrl = 'https://github.com/ckeditor/ckeditor5/issues';

	const message = [
		'Oops, something went wrong!',
		`Please, report the following error on ${ issueUrl } with the build id "r6g0q5nvvgic-9qp1jqlqjnqg" and the error stack trace:`
	].join( '\n' );

	console.error( message );
	console.error( error );
}

document.querySelectorAll('.reply-button').forEach(button => {
    button.addEventListener('click', function(event) {
        event.preventDefault();
        const postId = this.getAttribute('data-post-id');
        const replyId = this.getAttribute('data-reply-id');
        const replyAuthor = this.getAttribute('data-reply-user');

        let id = replyId ? 'reply-' + replyId : 'post-' + postId;
        if (ckInstances[id] && ckInstances[id].editor) {
            const editorData = ckInstances[id].editor.getData();
            if (window.watchdog && window.watchdog.editor) {
                const mainEditor = window.watchdog.editor;
                const currentData = mainEditor.getData();
                const replyBlock = `<p><blockquote><strong>Replying to ${replyAuthor}:</strong><br>${editorData}</blockquote></p>`;
                const combinedData = currentData + replyBlock;
                mainEditor.setData(combinedData);

				const editorContainer = document.getElementById('new-reply');
				editorContainer.scrollIntoView({behavior: 'smooth'});
            }
        }
    });
});

document.getElementById('btn-submit-post').addEventListener('click', () => {
	var editor = window.watchdog.editor;
	if (editor.getData().length == 0) {
		const toast = document.getElementById('empty-reply-toast');
		toast.classList.remove('hidden');
		setTimeout(function() {
			toast.classList.add('hidden');
		}, 5000);
		return;
	}

    document.getElementById('submit-post-modal').showModal();
});

document.getElementById('btn-submit-post-modal-yes').addEventListener('click', () => {
    var editor = window.watchdog.editor;
    var postData = editor.getData();

    $.ajax({
        type: 'POST',
        url: submitReplyURL.replace('0', postID),
        data: {
            'csrfmiddlewaretoken': csrfToken,
            'post_id': postID,
            'content': postData,
        },
        success: function (data) {
            if (data.success) {
                var membershipHtml = '';
                data.reply.author.memberships.forEach(function(membership) {
                    membershipHtml += `<kbd class="kbd kbd-sm" style="${membership.style}">${membership.name}</kbd>&nbsp;`;
                });

                var newReply = `
                    <div class="row row-editor mt-2">
                        <div class="editor-container">
                            <div class="p-3 mt-2 border border-gray-800 author-panel">
                                <div class="flex items-center space-x-4">
                                    <img src="${data.reply.author.profile_pic}" alt="${data.reply.author.name}" class="w-16 h-16 rounded-md border-2 border-gray-600"/>
                                    <div>
                                        <div class="text-white font-bold">
                                            ${data.reply.author.name_with_color}<br>
                                            ${membershipHtml}
                                        </div>
                                    </div>
                                </div>
                            </div> 
                            <div class="editor-reply-${data.reply.id}">
                                ${data.reply.content}
                            </div>
                            <div id="word-count" class="flex justify-between items-center">
                                <div class="text-xs">
                                    Words: <span id="word-count-body-reply-${data.reply.id}"></span><br>
                                    Characters: <span id="character-count-body-reply-${data.reply.id}"></span>
                                </div>
                                <div class="text-end mr-2"> 
                                    <div>
                                        <a href="#" class="link link-primary text-orange-500 no-underline" id="report-button" data-post-id="${data.reply.id}">Report</a>
                                        ·
                                        <a href="#" class="link link-primary text-orange-500 no-underline">
                                            Like
                                        </a>
                                        ·
                                        <button class="link link-primary text-orange-500 no-underline reply-button" id="reply-button" data-reply-id="${data.reply.id}" data-reply-user="${data.reply.author.name}">Reply</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                document.querySelector('.replies-container').innerHTML += newReply;
                initializeEditor('.editor-reply-' + data.reply.id, 'word-count-body-reply-' + data.reply.id, 'character-count-body-reply-' + data.reply.id, 'reply', data.reply.id);
                editor.setData('');
            }
        }
    });
});